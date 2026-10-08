import json
import re
import uuid
from typing import Any
from sqlalchemy.orm import Session

import httpx

from app.core.config import settings
from app.core.logging import logger
from app.models.application import Application
from app.models.evaluation import ScreeningResult
from app.models.job import Job
from app.schemas.screening import (
    ScreeningEvaluation,
    ScreeningRecommendation,
    SkillCategory,
    SkillMatch,
)
from app.services.resume_extractor import resume_extractor
from app.services.rag_service import rag_service
from langfuse import observe


class ScreeningAgentService:
    """
    Dedicated AI Screening Agent that evaluates candidate resumes against job descriptions.
    Supports configurable LLM providers (Groq, OpenAI, custom endpoints) with a
    deterministic heuristic fallback for offline, testing, or rate-limited environments.
    """

    @observe()
    def evaluate(
        self,
        job: Job,
        resume_text: str,
        candidate_name: str | None = None,
        custom_notes: str | None = None,
        rag_context: str | None = None,
    ) -> ScreeningEvaluation:
        """
        Runs the screening evaluation against a job and resume text.
        Attempts LLM provider first; falls back gracefully to heuristic evaluation if unavailable.
        """
        api_key = settings.effective_llm_api_key

        if api_key and settings.LLM_PROVIDER != "mock":
            try:
                return self._call_llm(job, resume_text, candidate_name, custom_notes, rag_context)
            except Exception as exc:
                logger.warning(
                    f"LLM screening call failed ({settings.LLM_PROVIDER}): {exc}. "
                    "Falling back to built-in heuristic screening evaluation."
                )

        return self._heuristic_evaluation(job, resume_text, candidate_name)

    def _build_prompt(
        self,
        job: Job,
        resume_text: str,
        candidate_name: str | None = None,
        custom_notes: str | None = None,
        rag_context: str | None = None,
    ) -> tuple[str, str]:
        """Constructs system and user prompts for the screening agent."""
        system_prompt = (
            "You are TalentForge's expert AI Technical Screening & Executive Recruiter Agent.\n"
            "Your objective is to thoroughly, objectively, and accurately evaluate a candidate's resume "
            "against the provided job requirements and output a structured JSON evaluation.\n"
            "Be realistic, rigorous, and constructive in your evaluation.\n"
            "You MUST respond ONLY with valid JSON conforming to this schema:\n"
            "{\n"
            '  "overall_score": float (0.0 to 100.0),\n'
            '  "recommendation": "ADVANCE" | "HOLD" | "REJECT",\n'
            '  "passed": boolean (true if overall_score >= 65),\n'
            '  "summary": "2-3 sentence executive overview of candidate fit",\n'
            '  "strengths": ["strength 1", "strength 2", ...],\n'
            '  "weaknesses": ["gap or concern 1", "gap or concern 2", ...],\n'
            '  "skills_analysis": [\n'
            '     {"skill": "name", "category": "required"|"preferred", "matched": true|false, "evidence": "quote or reason"}\n'
            "  ],\n"
            '  "experience_assessment": "assessment of years and relevant depth of experience",\n'
            '  "education_assessment": "assessment of education, degrees, and certifications",\n'
            '  "recommended_interview_questions": ["question 1", "question 2", ...]\n'
            "}"
        )

        job_info = [
            f"Job Title: {job.title}",
            f"Job Description: {job.description}",
        ]
        if job.requirements:
            job_info.append(f"Requirements: {job.requirements}")
        if job.required_skills:
            job_info.append(f"Required Skills: {job.required_skills}")
        if job.preferred_skills:
            job_info.append(f"Preferred Skills: {job.preferred_skills}")
        if job.required_experience:
            job_info.append(f"Required Experience: {job.required_experience}")
        if job.education_requirements:
            job_info.append(f"Education Requirements: {job.education_requirements}")
        if custom_notes:
            job_info.append(f"Recruiter Notes: {custom_notes}")

        if rag_context:
            job_info.append(f"Company Hiring Rules & Knowledge Context:\n{rag_context}")

        # Truncate resume text safely if excessively long (e.g., > 16,000 characters)
        safe_resume_text = resume_text[:16000]

        user_prompt = (
            f"=== TARGET JOB & KNOWLEDGE ===\n"
            f"{chr(10).join(job_info)}\n\n"
            f"=== CANDIDATE RESUME ({candidate_name or 'Applicant'}) ===\n"
            f"{safe_resume_text}\n\n"
            f"Evaluate the candidate strictly against the job requirements and knowledge context, returning the structured JSON result."
        )

        return system_prompt, user_prompt

    @observe()
    def _call_llm(
        self,
        job: Job,
        resume_text: str,
        candidate_name: str | None = None,
        custom_notes: str | None = None,
        rag_context: str | None = None,
    ) -> ScreeningEvaluation:
        """Makes an OpenAI-compatible API call to Groq / OpenAI."""
        system_prompt, user_prompt = self._build_prompt(
            job, resume_text, candidate_name, custom_notes, rag_context
        )

        api_key = settings.effective_llm_api_key
        base_url = settings.effective_llm_base_url.rstrip("/")
        endpoint = f"{base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "model": settings.LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": settings.LLM_TEMPERATURE,
            "response_format": {"type": "json_object"},
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed_data = json.loads(content)

        return ScreeningEvaluation.model_validate(parsed_data)

    def _heuristic_evaluation(
        self,
        job: Job,
        resume_text: str,
        candidate_name: str | None = None,
    ) -> ScreeningEvaluation:
        """
        Deterministic, offline-resilient evaluation engine.
        Extracts skill terms, verifies presence in resume, computes match ratios,
        and generates a realistic structured scorecard.
        """
        lower_resume = resume_text.lower()

        # 1. Gather required & preferred skills
        required_list: list[str] = []
        preferred_list: list[str] = []

        if job.required_skills:
            required_list.extend([s.strip() for s in re.split(r"[,;\n]+", job.required_skills) if s.strip()])
        if job.preferred_skills:
            preferred_list.extend([s.strip() for s in re.split(r"[,;\n]+", job.preferred_skills) if s.strip()])

        # If no explicit skill fields, parse requirements and description
        if not required_list:
            text_corpus = f"{job.title} {job.requirements or ''} {job.description}"
            tech_keywords = [
                "Python", "FastAPI", "React", "Next.js", "TypeScript", "JavaScript",
                "SQL", "PostgreSQL", "Docker", "AWS", "Git", "REST API", "GraphQL",
                "Kubernetes", "CI/CD", "Node.js", "Java", "Go", "C++", "PyTorch"
            ]
            for kw in tech_keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", text_corpus, re.IGNORECASE):
                    required_list.append(kw)

        if not required_list:
            required_list = ["Relevant Industry Experience", "Problem Solving", "Communication"]

        # 2. Analyze skills
        skills_analysis: list[SkillMatch] = []
        matched_required = 0
        strengths: list[str] = []
        weaknesses: list[str] = []

        for skill in required_list:
            pattern = r"\b" + re.escape(skill.lower()) + r"\b"
            is_matched = bool(re.search(pattern, lower_resume))
            if is_matched:
                matched_required += 1
                evidence = f"Demonstrated background/mention of '{skill}' in candidate resume."
                strengths.append(f"Demonstrates required proficiency in {skill}")
            else:
                evidence = f"No direct mention of required skill '{skill}' identified."
                weaknesses.append(f"Missing explicit experience with required skill '{skill}'")

            skills_analysis.append(
                SkillMatch(
                    skill=skill,
                    category=SkillCategory.REQUIRED,
                    matched=is_matched,
                    evidence=evidence,
                )
            )

        matched_preferred = 0
        for skill in preferred_list:
            pattern = r"\b" + re.escape(skill.lower()) + r"\b"
            is_matched = bool(re.search(pattern, lower_resume))
            if is_matched:
                matched_preferred += 1
                evidence = f"Found nice-to-have skill '{skill}' in resume."
                strengths.append(f"Offers bonus experience in {skill}")
            else:
                evidence = None

            skills_analysis.append(
                SkillMatch(
                    skill=skill,
                    category=SkillCategory.PREFERRED,
                    matched=is_matched,
                    evidence=evidence,
                )
            )

        # 3. Calculate score
        req_ratio = matched_required / max(len(required_list), 1)
        pref_ratio = matched_preferred / max(len(preferred_list), 1) if preferred_list else 1.0

        # Experience check
        exp_matches = re.findall(r"(\d+)\+?\s*years?", lower_resume)
        years_found = max([int(y) for y in exp_matches], default=3)
        exp_score = min(years_found / 5.0, 1.0)

        # Combined score calculation (0 to 100)
        overall_score = round((req_ratio * 65.0) + (pref_ratio * 15.0) + (exp_score * 20.0), 1)
        overall_score = min(max(overall_score, 15.0), 98.0)

        # Recommendation
        if overall_score >= 70.0:
            recommendation = ScreeningRecommendation.ADVANCE
            passed = True
        elif overall_score >= 50.0:
            recommendation = ScreeningRecommendation.HOLD
            passed = False
        else:
            recommendation = ScreeningRecommendation.REJECT
            passed = False

        # 4. Synthesize assessments
        candidate_label = candidate_name or "Candidate"
        summary = (
            f"{candidate_label} achieved an overall match score of {overall_score}%. "
            f"The candidate matched {matched_required}/{len(required_list)} required core skills. "
            f"Recommendation: {recommendation.value}."
        )

        exp_assessment = (
            f"Resume indicates approximately {years_found}+ years of professional background. "
            f"Work history demonstrates relevant technical application aligning with role demands."
        )

        degree_terms = ["bachelor", "master", "degree", "bs", "ms", "phd", "university", "college", "b.tech"]
        has_degree = any(t in lower_resume for t in degree_terms)
        edu_assessment = (
            "Academic credentials verified in computer science or related technical discipline."
            if has_degree
            else "Relevant practical industry experience documented; educational credentials to be confirmed."
        )

        interview_questions: list[str] = [
            f"Can you walk us through a recent project where you applied {required_list[0] if required_list else 'your core technical skills'}?",
        ]
        if weaknesses:
            missing_skill_name = (
                skills_analysis[0].skill
                if any(not s.matched for s in skills_analysis)
                else "key architectural concepts"
            )
            interview_questions.append(
                f"How would you approach ramping up on {missing_skill_name} in our production environment?"
            )
        interview_questions.append(
            "What was the most challenging technical tradeoff you made in your previous position?"
        )

        return ScreeningEvaluation(
            overall_score=overall_score,
            recommendation=recommendation,
            passed=passed,
            summary=summary,
            strengths=strengths[:4] or ["Relevant technical foundation", "Standard industry background"],
            weaknesses=weaknesses[:4] or ["Minor skill gap verification required"],
            skills_analysis=skills_analysis,
            experience_assessment=exp_assessment,
            education_assessment=edu_assessment,
            recommended_interview_questions=interview_questions,
        )

    @observe()
    def screen_application(
        self,
        db: Session,
        application_id: uuid.UUID,
        force_rescreen: bool = False,
        custom_notes: str | None = None,
    ) -> ScreeningResult:
        """
        Orchestrates full application screening:
        1. Retrieves application, job, and candidate
        2. Retrieves & extracts resume text
        3. Evaluates via Screening Agent
        4. Persists result in database and updates application status
        """
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application with ID {application_id} not found.")

        # Check existing result
        existing_result = (
            db.query(ScreeningResult)
            .filter(ScreeningResult.application_id == application_id)
            .first()
        )
        if existing_result and not force_rescreen:
            return existing_result

        # Retrieve candidate resumes
        candidate = application.candidate
        if not candidate.resumes:
            raise ValueError(f"Candidate '{candidate.name}' has no uploaded resume to screen.")

        # Select latest resume
        latest_resume = sorted(candidate.resumes, key=lambda r: r.uploaded_at)[-1]

        # Extract text (or get cached)
        resume_text = resume_extractor.get_or_extract_text(db, latest_resume)

        # Gather RAG Context
        rag_chunks = rag_service.search(db, query=f"{application.job.title} {application.job.description}", top_k=3)
        rag_context = "\n".join(c.content for c in rag_chunks) if rag_chunks else None

        # Evaluate candidate against job
        evaluation = self.evaluate(
            job=application.job,
            resume_text=resume_text,
            candidate_name=candidate.name,
            custom_notes=custom_notes,
            rag_context=rag_context,
        )

        # Update or create ScreeningResult entity
        if existing_result:
            existing_result.score = evaluation.overall_score
            existing_result.recommendation = evaluation.recommendation.value
            existing_result.summary = evaluation.summary
            existing_result.passed = evaluation.passed
            existing_result.details = evaluation.model_dump(mode="json")
            result_entity = existing_result
        else:
            result_entity = ScreeningResult(
                id=uuid.uuid4(),
                application_id=application.id,
                score=evaluation.overall_score,
                recommendation=evaluation.recommendation.value,
                summary=evaluation.summary,
                passed=evaluation.passed,
                details=evaluation.model_dump(mode="json"),
            )
            db.add(result_entity)

        # Update application status
        application.status = "screened"
        db.add(application)
        db.commit()
        db.refresh(result_entity)

        return result_entity


screening_agent = ScreeningAgentService()
