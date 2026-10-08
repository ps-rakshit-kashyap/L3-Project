# Phase 9: Langfuse Integration & Observability

## Overview
TalentForge uses **Langfuse** for end-to-end LLM observability, tracking everything from raw prompts and token costs to multi-agent orchestration flows and evaluation pipelines.

## Configuration
Add the following to your `.env` file:
```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```
*Note: Do not expose these keys to the frontend.*

## Tracing Architecture
We use the official `langfuse.decorators` `@observe` decorator to automatically construct trace hierarchies. 

### LLM Tracing
All LLM generation runs through `app.services.llm_client.call_llm_structured`.
This automatically captures:
- `model` (e.g. `llama-3.3-70b-versatile`)
- `input` (system & user prompts)
- `output` (JSON result)
- `usage` (input, output, and total tokens)
- `cost` (computed automatically by Langfuse if supported)
- `latency`
- `errors`

### Agent & Orchestration Tracing
By stacking `@observe()` decorators, Langfuse automatically correlates nested executions.
A typical trace hierarchy looks like this:
```
Trace
 └── Orchestration Run (e.g. COMPLETE_INTERVIEW)
      └── FinalEvaluator (Agent Execution)
           └── call_llm_structured (LLM Generation)
```
Covered agents:
- Resume Screening
- Technical Evaluator
- Problem Solving Evaluator
- Communication Evaluator
- Role Fit Evaluator
- Question Generator
- Final Evaluator

### Phase 8 Evaluation Integration
The `EvaluationEngine.run_evaluation` method is also decorated with `@observe()`. When regression datasets are executed via the CLI or API, all AI calls made during the test run are cleanly siloed and observable in the Langfuse dashboard, allowing developers to inspect prompt failures and regressions visually.

## Error Handling
Observability degrades gracefully. If Langfuse keys are absent or the Langfuse cloud is unreachable, the `@observe()` decorators bypass tracking and application logic continues unabated.

## Swagger API
Health endpoints are provided for runtime introspection:
- `GET /api/v1/observability/health`
- `GET /api/v1/observability/config`
