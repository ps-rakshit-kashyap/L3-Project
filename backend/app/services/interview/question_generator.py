from typing import List
from app.services.llm_client import call_llm_structured
from app.schemas.interview import InterviewQuestionCreate
from app.prompts.interview.question_generation import QUESTION_GENERATION_PROMPT

def generate_questions(candidate_context: str, job_context: str, rubric_context: str) -> List[InterviewQuestionCreate]:
    questions = []
    categories = ["TECHNICAL", "PROBLEM_SOLVING", "COMMUNICATION", "ROLE_FIT"]
    for i, category in enumerate(categories):
        user_prompt = f"Category requested: {category}\n\nJob Context:\n{job_context}\n\nCandidate Resume:\n{candidate_context}\n\nRubric:\n{rubric_context}"
        res = call_llm_structured(QUESTION_GENERATION_PROMPT, user_prompt, InterviewQuestionCreate)
        if res:
            res.order_index = i
            questions.append(res)
        else:
            # Fallback
            questions.append(InterviewQuestionCreate(
                question=f"Fallback {category} question: Tell me about your experience.",
                category=category,
                difficulty="MEDIUM",
                competency="General",
                evaluation_criteria=["Clear answer"],
                order_index=i
            ))
    return questions
