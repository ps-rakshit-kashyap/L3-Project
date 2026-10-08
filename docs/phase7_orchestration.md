# Phase 7: Multi-Agent Orchestration & A2A

## Orchestration Architecture
The TalentForge Interview Orchestrator (`app.services.orchestration_service`) acts as the centralized brain for managing the AI-powered interview state machine. 
It wraps the underlying Phase 6 generative agents into stateful, traceable workflows without duplicating core agent logic. 

The Orchestrator defines three distinct workflow types:
1. `GENERATE_QUESTIONS`
2. `EVALUATE_ANSWER`
3. `COMPLETE_INTERVIEW`

All orchestration states and child agent executions are persisted relationally in `orchestration_runs` and `agent_executions` tables.

## Agent Responsibilities
- **QuestionGenerator**: Reads the RAG job context + candidate resume and emits specialized interview questions.
- **TechnicalEvaluator**: Scores candidate technical depth and correctness.
- **ProblemSolvingEvaluator**: Scores candidate's approach, structure, and logic.
- **CommunicationEvaluator**: Scores clarity, tone, and conciseness.
- **RoleFitEvaluator**: Scores alignment with team values and company culture.
- **FinalEvaluator**: Synthesizes output from all above agents into a finalized hire/no-hire recommendation.

## Agent-to-Agent (A2A) Communication
The orchestrator leverages direct typed Python function invocations wrapped over robust Pydantic contracts (`AgentRequest`, `AgentResponse`, etc.) located in `app.schemas.orchestration`.
Because all agents reside in the same FastAPI monolith, this approach is significantly faster and less flaky than network HTTP calls (Ponytail architecture).
However, for debugging and external invocation, all agents also expose direct REST JSON endpoints under `/api/v1/agents/...`.

## Workflow & Parallel Execution
During `EVALUATE_ANSWER`, the orchestrator dispatches the answer to the `Technical`, `Problem Solving`, `Communication`, and `Role Fit` agents simultaneously. 
It uses Python's `concurrent.futures.ThreadPoolExecutor` to await all LLM evaluators in parallel before continuing. 

## Failure & Retry Behavior
Agent failures are cleanly captured inside a `try/except` block and recorded into the `agent_executions` table with the `FAILED` status and exception stack trace.
Failures of individual agents do not crash the FastAPI application but cause the parent `OrchestrationRun` to halt with `FAILED`.
Users can inspect the error message via the `/status` or `/trace` endpoints and retry the API call if necessary.

## Security & RBAC Model
The orchestration endpoints (`/api/v1/orchestration/...`) inherit the standard FastAPI `current_user: User = Depends(get_current_user)` authentication guard.
Furthermore, a resource ownership verification (`check_interview_access`) guarantees that `CANDIDATE` roles can only view and orchestrate interviews bound to their specific Candidate ID.

## Swagger Endpoints
The following endpoints are available under the FastAPI Swagger UI:
- `POST /api/v1/orchestration/interviews/{id}/generate`
- `POST /api/v1/orchestration/interviews/{id}/evaluate`
- `POST /api/v1/orchestration/interviews/{id}/complete`
- `GET /api/v1/orchestration/interviews/{id}/status`
- `GET /api/v1/orchestration/interviews/{id}/trace`
