from app.schemas.interview import EvaluatorResult
from app.services.interview.evaluators import evaluate_technical, evaluate_problem_solving, evaluate_communication, evaluate_role_fit

def evaluate_answer(question: str, answer: str, candidate_context: str, job_context: str, rubric_context: str, category: str) -> EvaluatorResult:
    if category == "TECHNICAL":
        return evaluate_technical(question, answer, candidate_context, job_context, rubric_context)
    elif category == "PROBLEM_SOLVING":
        return evaluate_problem_solving(question, answer, candidate_context, job_context, rubric_context)
    elif category == "COMMUNICATION":
        return evaluate_communication(question, answer, candidate_context, job_context, rubric_context)
    else:
        return evaluate_role_fit(question, answer, candidate_context, job_context, rubric_context)
