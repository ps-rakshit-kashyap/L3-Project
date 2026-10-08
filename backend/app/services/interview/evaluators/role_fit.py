from app.services.llm_client import call_llm_structured
from app.schemas.interview import EvaluatorResult
from langfuse import observe

PROMPT = """You are an HR / Role-Fit Interview Evaluator. 
Evaluate role alignment, behavioral evidence, teamwork, and ownership based on the answer.
Do not infer personal attributes not provided. Avoid protected attribute inference.
Output JSON with: score (float 0-100), strengths (list of strings), weaknesses (list of strings), evidence (string), rationale (string)."""

@observe()
def evaluate(question: str, answer: str, candidate_context: str, job_context: str, rubric_context: str) -> EvaluatorResult:
    user_prompt = f"Job Context:\n{job_context}\n\nCandidate Context:\n{candidate_context}\n\nRubric:\n{rubric_context}\n\nQuestion:\n{question}\n\nAnswer:\n{answer}"
    res = call_llm_structured(PROMPT, user_prompt, EvaluatorResult)
    return res or EvaluatorResult(score=75.0, strengths=["Aligns generally"], weaknesses=["Needs more behavioral evidence"], evidence="Fallback", rationale="Fallback executed due to LLM error")
