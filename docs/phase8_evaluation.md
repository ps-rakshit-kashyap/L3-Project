# Phase 8: Evaluation & Quality Framework

## Evaluation Architecture
The Evaluation Framework ensures that TalentForge's LLM outputs remain robust, accurate, and aligned with rubrics during prompt/model updates.
It employs a deterministic evaluation engine that tests Agent executions (like the `TechnicalEvaluator`) against a curated JSON benchmark dataset (`data/eval_dataset.json`).

## Dataset Format
The framework consumes JSON arrays mapped to the `EvaluationCase` schema:
```json
{
    "case_id": "test-tech-1",
    "task_type": "technical_eval",
    "input_context": {
        "question": "What is REST?",
        "answer": "Representational State Transfer",
        "resume_text": "Backend Dev",
        "job_context": "Software Engineer",
        "rubric": "Must know HTTP methods."
    },
    "expected_output": {
        "score_min": 7.0,
        "score_max": 10.0
    }
}
```

## Metrics
Metrics are primarily deterministic for speed and reliability, avoiding LLM-as-a-judge overhead:
- **score_match**: Verifies if the LLM-generated score falls within the benchmark's `[score_min, score_max]` threshold.
- **schema_valid**: Ensures the Pydantic structured output contains all required fields (`score`, `strengths`, `rationale`).
- **latency_ms**: Times the agent invocation.
- **error**: Flags exceptions/timeouts.

## CLI Execution
Run the evaluation natively via CLI to test models or prompts locally:
```bash
uv run python -m app.evaluation.run --dataset data/eval_dataset.json --agent technical_eval --model gpt-4
```

## Swagger API
Evaluation runs can also be triggered and inspected via the REST API (secured for `ADMIN`/`RECRUITER` roles):
- `POST /api/v1/evaluations/runs` (Execute dataset against an agent)
- `GET /api/v1/evaluations/runs/{id}` (Get run summary)
- `GET /api/v1/evaluations/runs/{id}/results` (Get detailed case metrics)

## Persistence
Runs and metrics are captured in PostgreSQL tables:
- `evaluation_runs`
- `evaluation_results`

This lightweight normalized schema provides a historic trace of accuracy and regression over time.
