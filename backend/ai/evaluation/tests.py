from django.core.cache import cache
from django.test import TestCase

from .cases import EVALUATION_CASES
from .fixtures import EvaluationFixtureFactory
from .runner import EvaluationRunner, stability_score, summarize


class EvaluationRunnerTests(TestCase):
    def setUp(self):
        cache.clear()
        self.fixture = EvaluationFixtureFactory().create()
        self.results = EvaluationRunner(self.fixture).run()

    def test_deterministic_benchmark_passes_objective_checks(self):
        failed = [result.as_dict() for result in self.results if not result.passed]
        self.assertEqual(failed, [])

    def test_semantic_cases_include_relevant_candidate_in_pool(self):
        semantic_results = [
            result for result in self.results
            if result.case.category == "semantic"
        ]
        self.assertTrue(semantic_results)
        self.assertTrue(all(
            result.checks["semantic_candidate_presence"]
            for result in semantic_results
        ))

    def test_personalized_profiles_receive_different_results(self):
        results_by_key = {result.case.key: result for result in self.results}
        item_sets = {
            key: tuple(result.trace["final_menu_item_ids"])
            for key, result in results_by_key.items()
            if key in {"usual_italian", "usual_japanese", "usual_vegetarian"}
        }
        self.assertEqual(len(item_sets), 3)
        self.assertEqual(len(set(item_sets.values())), 3)

    def test_summary_reports_diversity_and_failures(self):
        summary = summarize(self.results)
        self.assertEqual(summary["total_cases"], len(EVALUATION_CASES))
        self.assertEqual(summary["failed_cases"], 0)
        self.assertGreater(summary["diversity"]["unique_item_ratio"], 0)

    def test_deterministic_runs_are_stable(self):
        repeated_results = EvaluationRunner(self.fixture).run()
        self.assertEqual(stability_score(self.results, repeated_results), 1.0)

    def test_surprise_variation_metric_detects_repeated_result_sets(self):
        variation = EvaluationRunner(self.fixture).measure_surprise_variation()
        self.assertEqual(variation["runs"], 3)
        self.assertEqual(variation["unique_result_sets"], 1)
        self.assertFalse(variation["varied"])