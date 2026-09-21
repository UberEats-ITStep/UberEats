import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ai.evaluation.cases import EVALUATION_CASES
from ai.evaluation.fixtures import EvaluationFixtureFactory
from ai.evaluation.runner import EvaluationRunner, stability_score, summarize


class Command(BaseCommand):
    help = "Run BiteUp's repeatable AI recommendation quality benchmark."

    def add_arguments(self, parser):
        parser.add_argument(
            "--category",
            choices=sorted({case.category for case in EVALUATION_CASES}),
            help="Run one evaluation category only.",
        )
        parser.add_argument(
            "--format",
            choices=("text", "json"),
            default="text",
            help="Output format.",
        )
        parser.add_argument(
            "--live-llm",
            action="store_true",
            help="Use the configured Groq service instead of the deterministic benchmark client.",
        )
        parser.add_argument(
            "--fail-on-failure",
            action="store_true",
            help="Exit with an error when any benchmark case fails.",
        )

    def handle(self, *args, **options):
        live_llm = options["live_llm"]
        if live_llm and not getattr(settings, "GROQ_API_KEY", None):
            raise CommandError("GROQ_API_KEY must be configured when using --live-llm.")

        cases = tuple(
            case for case in EVALUATION_CASES
            if not options["category"] or case.category == options["category"]
        )
        with transaction.atomic():
            fixture = EvaluationFixtureFactory().create()
            runner = EvaluationRunner(fixture, live_llm=live_llm)
            results = runner.run(cases)
            repeated_results = runner.run(cases)
            summary = summarize(
                results,
                stability=stability_score(results, repeated_results),
                surprise_variation=runner.measure_surprise_variation(),
            )
            transaction.set_rollback(True)

        report = {
            "mode": "live_llm" if live_llm else "deterministic",
            "summary": summary,
            "failures": [result.as_dict() for result in results if not result.passed],
        }
        if options["format"] == "json":
            self.stdout.write(json.dumps(report, ensure_ascii=False, indent=2, default=str))
        else:
            self._write_text_report(report)

        if options["fail_on_failure"] and summary["failed_cases"]:
            raise CommandError("One or more AI evaluation cases failed.")

    def _write_text_report(self, report):
        summary = report["summary"]
        self.stdout.write("BiteUp AI Evaluation")
        self.stdout.write("=" * 30)
        self.stdout.write(f"Mode:               {report['mode']}")
        self.stdout.write(f"Total cases:        {summary['total_cases']}")
        self.stdout.write(f"Passed:             {summary['passed_cases']}")
        self.stdout.write(f"Failed:             {summary['failed_cases']}")
        self.stdout.write("")
        self.stdout.write("Checks:")
        for key, score in summary["checks"].items():
            self.stdout.write(f"  {key}: {score}%")
        self.stdout.write(f"Semantic relevance: {summary['semantic_relevance']}%")
        diversity = summary["diversity"]
        self.stdout.write(
            "Diversity:          "
            f"{diversity['unique_item_ratio']} unique-item ratio "
            f"({diversity['unique_items']} items, "
            f"{diversity['unique_restaurants']} restaurants)"
        )
        self.stdout.write(f"Stability:          {summary['stability']}")
        surprise = summary["surprise_variation"]
        self.stdout.write(
            "Surprise variation: "
            f"{surprise['unique_result_sets']}/{surprise['runs']} unique result sets "
            f"(varied={surprise['varied']})"
        )
        if report["failures"]:
            self.stdout.write("")
            self.stdout.write("Failures:")
            for failure in report["failures"]:
                failed_checks = [
                    key for key, passed in failure["checks"].items()
                    if not passed
                ]
                self.stdout.write(
                    f"  {failure['case']}: {', '.join(failed_checks)}"
                )