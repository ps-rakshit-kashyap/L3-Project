from typing import List
from app.services.llm_client import call_llm_structured
from app.schemas.interview import EvaluatorResult, FinalEvaluationResult
from app.prompts.interview.final_evaluation import FINAL_EVALUATION_PROMPT

def evaluate_final(evaluations: List[dict]) -> FinalEvaluationResult:
    user_prompt = f"Evaluations:\n{evaluations}"
    res = call_llm_structured(FINAL_EVALUATION_PROMPT, user_prompt, FinalEvaluationResult)
    if res:
        return res
    # Deterministic fallback
    tech = next((e['score'] for e in evaluations if e['evaluator_type'] == 'TECHNICAL'), 75.0)
    prob = next((e['score'] for e in evaluations if e['evaluator_type'] == 'PROBLEM_SOLVING'), 75.0)
    comm = next((e['score'] for e in evaluations if e['evaluator_type'] == 'COMMUNICATION'), 75.0)
    fit = next((e['score'] for e in evaluations if e['evaluator_type'] == 'ROLE_FIT'), 75.0)
    overall = (tech * 0.3) + (prob * 0.25) + (comm * 0.2) + (fit * 0.25)
    return FinalEvaluationResult(
        technical_score=tech, problem_solving_score=prob, communication_score=comm, role_fit_score=fit,
        overall_score=overall, strengths=[], weaknesses=[], evidence="Fallback", summary="Fallback", recommendation="REVIEW"
    )
