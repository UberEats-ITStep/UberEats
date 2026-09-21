from dataclasses import dataclass

from restaurants.models import MenuItem

from ai.services import GroqClient, RecommendationOrchestrator

from .cases import EVALUATION_CASES, EvaluationCase
from .fixtures import EvaluationFixture


@dataclass
class CaseResult:
    case: EvaluationCase
    checks: dict[str, bool]
    trace: dict
    result: dict
    relevance_score: float | None

    @property
    def passed(self) -> bool:
        return all(self.checks.values())

    def as_dict(self) -> dict:
        return {
            "case": self.case.key,
            "query": self.case.query,
            "category": self.case.category,
            "passed": self.passed,
            "checks": self.checks,
            "relevance_score": self.relevance_score,
            "result": self.result,
            "trace": self.trace,
        }


class BenchmarkGroqClient:
    """A deterministic client used to test the pipeline without a network call."""

    def __init__(self, case: EvaluationCase, fixture: EvaluationFixture):
        self.case = case
        self.fixture = fixture
        self.call_count = 0

    def chat_completion(self, system_prompt, user_content, temperature=0.0):
        self.call_count += 1
        if self.call_count == 1:
            return self.case.intent
        return {
            "recommendations": [
                {
                    "menu_item_id": self.fixture.items[item_key].id,
                    "reason": "Benchmark-ranked candidate.",
                }
                for item_key in self.case.relevant_item_keys[:4]
            ],
            "summary": "Evaluation recommendation.",
        }


class EvaluationRunner:
    def __init__(self, fixture: EvaluationFixture, live_llm=False):
        self.fixture = fixture
        self.live_llm = live_llm

    def run(self, cases=EVALUATION_CASES) -> list[CaseResult]:
        return [self.run_case(case) for case in cases]

    def run_case(self, case: EvaluationCase) -> CaseResult:
        client = GroqClient() if self.live_llm else BenchmarkGroqClient(case, self.fixture)
        result, trace = RecommendationOrchestrator(client=client).process_with_trace(
            query=case.query,
            user=self.fixture.users[case.user_profile],
        )
        return self._evaluate(case, result, trace)

    def measure_surprise_variation(self, repeats=3) -> dict:
        surprise_case = next(
            case for case in EVALUATION_CASES
            if case.key == "surprise_cold_start"
        )
        result_sets = [
            tuple(self.run_case(surprise_case).trace["final_menu_item_ids"])
            for _ in range(repeats)
        ]
        unique_sets = len(set(result_sets))
        return {
            "runs": repeats,
            "unique_result_sets": unique_sets,
            "unique_set_ratio": round(unique_sets / repeats, 2),
            "varied": unique_sets > 1,
        }

    def _evaluate(self, case: EvaluationCase, result: dict, trace: dict) -> CaseResult:
        item_ids = trace["final_menu_item_ids"]
        items = list(
            MenuItem.objects.filter(id__in=item_ids)
            .select_related("restaurant")
        )
        item_by_id = {item.id: item for item in items}
        ordered_items = [item_by_id[item_id] for item_id in item_ids if item_id in item_by_id]
        expected = case.expected
        checks = {
            "result_count": len(item_ids) <= 4 and len(item_ids) == len(set(item_ids)),
            "grounding": all(
                item.is_available and item.restaurant.is_active
                for item in ordered_items
            ) and set(item_ids).issubset({candidate["id"] for candidate in trace["candidates"]}),
        }
        if "min_results" in expected:
            checks["minimum_results"] = len(item_ids) >= expected["min_results"]
        if "should_return_results" in expected:
            checks["expected_empty_result"] = bool(item_ids) == expected["should_return_results"]
        if "max_price" in expected:
            checks["max_price"] = all(item.price <= expected["max_price"] for item in ordered_items)
        if expected.get("is_vegetarian"):
            checks["vegetarian"] = all(item.is_vegetarian for item in ordered_items)
        if expected.get("is_vegan"):
            checks["vegan"] = all(item.is_vegan for item in ordered_items)

        expected_ids = {
            self.fixture.items[item_key].id
            for item_key in case.relevant_item_keys
        }
        if case.category == "semantic":
            checks["semantic_candidate_presence"] = bool(
                expected_ids & {candidate["id"] for candidate in trace["candidates"]}
            )
        if expected.get("personalized"):
            checks["personalization"] = bool(expected_ids & set(item_ids))
        if expected.get("cold_start"):
            checks["cold_start_fallback"] = bool(item_ids)

        relevance_scores = [
            case.relevance_labels[item_key]
            for item_key, item in self.fixture.items.items()
            if item.id in item_ids and item_key in case.relevance_labels
        ]
        relevance_score = (
            round(sum(relevance_scores) / (2 * len(relevance_scores)), 2)
            if relevance_scores
            else None
        )
        if expected.get("semantic_relevance"):
            checks["semantic_relevance"] = relevance_score is not None and relevance_score >= 0.5
        return CaseResult(
            case=case,
            checks=checks,
            trace=trace,
            result=result,
            relevance_score=relevance_score,
        )


def summarize(results: list[CaseResult], stability=None, surprise_variation=None) -> dict:
    def percentage(values):
        return round(100 * sum(values) / len(values), 1) if values else None

    check_values = {}
    for result in results:
        for key, value in result.checks.items():
            check_values.setdefault(key, []).append(value)
    discovery_ids = [
        item_id
        for result in results
        if result.case.category == "discovery"
        for item_id in result.trace["final_menu_item_ids"]
    ]
    discovery_restaurants = {
        recommendation["menu_item"]["restaurant"]["id"]
        for result in results
        if result.case.category == "discovery"
        for recommendation in result.result["recommendations"]
    }
    return {
        "total_cases": len(results),
        "passed_cases": sum(result.passed for result in results),
        "failed_cases": sum(not result.passed for result in results),
        "checks": {key: percentage(values) for key, values in sorted(check_values.items())},
        "semantic_relevance": percentage([
            result.relevance_score >= 0.5
            for result in results
            if result.relevance_score is not None
        ]),
        "diversity": {
            "unique_item_ratio": round(len(set(discovery_ids)) / len(discovery_ids), 2) if discovery_ids else None,
            "unique_items": len(set(discovery_ids)),
            "unique_restaurants": len(discovery_restaurants),
            "total_slots": len(discovery_ids),
        },
        "stability": stability,
        "surprise_variation": surprise_variation,
    }


def stability_score(
    baseline: list[CaseResult],
    repeated: list[CaseResult],
) -> float | None:
    repeated_ids = {
        result.case.key: tuple(result.trace["final_menu_item_ids"])
        for result in repeated
    }
    comparisons = [
        tuple(result.trace["final_menu_item_ids"])
        == repeated_ids.get(result.case.key)
        for result in baseline
    ]
    if not comparisons:
        return None
    return round(sum(comparisons) / len(comparisons), 2)