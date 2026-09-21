# BiteUp AI Recommendation Evaluation

## Purpose

This benchmark checks recommendation quality beyond an HTTP success response. It evaluates database grounding, explicit constraints, semantic candidate retrieval, personalization behavior, diversity, and repeat-run stability.

## Run the benchmark

From `backend/`:

```powershell
python manage.py evaluate_ai --fail-on-failure
```

The default mode uses a deterministic benchmark client and a temporary catalog. All fixture records are created inside a transaction that is rolled back, so the command does not change the active catalog or user data.

Useful options:

```powershell
python manage.py evaluate_ai --category semantic
python manage.py evaluate_ai --format json
python manage.py evaluate_ai --live-llm --fail-on-failure
```

`--live-llm` uses the configured Groq service and is intentionally opt-in because it has network, cost, and non-determinism implications.

## Dataset and users

`ai/evaluation/cases.py` contains the fixed requests and expected properties. The suite covers hard dietary and price constraints, semantic requests, discovery, cold-start behavior, three synthetic preference profiles, and deliberately contradictory requests.

`ai/evaluation/fixtures.py` builds a small controlled catalog and users with completed-order history. The profiles represent Italian/burger, Japanese, vegetarian, and cold-start users. This makes every run independent of production catalog randomness.

## Checks and metrics

- **Constraint correctness:** price, vegetarian, and vegan properties are verified directly against `MenuItem` records.
- **Grounding:** every final ID must be from the retrieved candidate pool, available, and owned by an active restaurant.
- **Result shape:** responses are deduplicated and limited to four recommendations.
- **Semantic retrieval:** the runner reads the candidate pool from the execution trace and measures whether labelled relevant items reached it before ranking.
- **Semantic relevance:** human-authored labels use `0` (irrelevant), `1` (somewhat relevant), and `2` (highly relevant). The reported score is normalized to `0..1`.
- **Personalization:** the same dinner request is run for distinct synthetic histories and must select profile-compatible items.
- **Diversity:** discovery queries report unique recommended items divided by total recommendation slots, plus distinct restaurants.
- **Stability:** the suite is run twice and compares final ordered item IDs case by case.
- **Surprise variation:** `Surprise me` is run three times for the same cold-start profile. The report shows the number of distinct ordered result sets instead of treating a repeated set as diverse.

Failures include the query, expected case category, deterministic checks, result payload, and full retrieval/ranking trace in JSON output. This lets the team identify whether a failure came from retrieval, ranking, or final validation.

## Deterministic vs LLM evaluation

Database grounding and hard constraints are deterministic checks. Semantic relevance is partly subjective; the compact labelled benchmark is a transparent reference set, not an objective universal truth. The deterministic mode validates retrieval and safeguards without external calls. Live mode evaluates the actual Groq intent/ranking output against the same rules and labels.

## Event tracking

The recommendation endpoint records `served` events. The frontend records `clicked` and carries the recommendation request ID to record `added_to_cart`. The API also accepts `ordered` events for checkout integration. Events retain the request ID, user, item, ranking position, timestamp, and (for served events) query, enabling later analysis of real user behavior.

## Limitations

The current retriever is structured ORM filtering plus tag/name/description matching. The benchmark isolates this stage so that a future embedding-based semantic retriever can be compared on candidate recall without changing the ranker contract. Human semantic labels are deliberately small and must be expanded or reviewed as the catalog grows. Live LLM scores can vary by model version and catalog state, so they should be recorded over time rather than treated as permanently deterministic.

The deterministic benchmark intentionally returns stable scripted ranking decisions. Therefore its surprise-variation value validates the metric rather than claiming production variety. Use `--live-llm` to measure whether the deployed ranker returns varied yet valid sets for repeated surprise requests.