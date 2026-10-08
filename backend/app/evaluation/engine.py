import json
import time
from typing import Any, Dict, Tuple
from sqlalchemy.orm import Session
from app.schemas.evaluation import EvaluationCase
from app.models.evaluation_framework import EvaluationRun, EvaluationResultLog
from app.services.interview.evaluators import evaluate_technical, evaluate_problem_solving, evaluate_communication, evaluate_role_fit
from datetime import UTC, datetime

class EvaluationEngine:
    def load_dataset(self, file_path: str) -> list[EvaluationCase]:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [EvaluationCase(**item) for item in data]

    def _execute_case(self, case: EvaluationCase) -> Tuple[Dict[str, Any], str | None]:
        agent_name = case.task_type
        args = case.input_context
        try:
            if agent_name == "technical_eval":
                res = evaluate_technical(args["question"], args["answer"], args.get("resume_text", ""), args.get("job_context", ""), args.get("rubric", ""))
                return res.model_dump(), None
            elif agent_name == "problem_solving_eval":
                res = evaluate_problem_solving(args["question"], args["answer"], args.get("resume_text", ""), args.get("job_context", ""), args.get("rubric", ""))
                return res.model_dump(), None
            else:
                return {}, f"Unknown agent {agent_name}"
        except Exception as e:
            return {}, str(e)

    def _evaluate_metrics(self, case: EvaluationCase, actual: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        expected = case.expected_output
        metrics = {}
        passed = True
        
        if "score_min" in expected and "score_max" in expected:
            score = actual.get("score", 0)
            ok = expected["score_min"] <= score <= expected["score_max"]
            metrics["score_match"] = ok
            if not ok:
                passed = False
                
        metrics["schema_valid"] = "score" in actual and "strengths" in actual
        if not metrics["schema_valid"]:
            passed = False
            
        return passed, metrics

    def run_evaluation(self, db: Session, dataset_path: str, agent_name: str, model_name: str = "mock") -> EvaluationRun:
        cases = self.load_dataset(dataset_path)
        
        run = EvaluationRun(
            agent_name=agent_name,
            dataset_name=dataset_path,
            model_name=model_name,
            status="RUNNING",
            total_cases=len(cases)
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        passed_count = 0
        for case in cases:
            start_t = time.time()
            actual_output, err = self._execute_case(case)
            latency = int((time.time() - start_t) * 1000)
            
            if err:
                passed = False
                metrics = {"error": True}
            else:
                passed, metrics = self._evaluate_metrics(case, actual_output)
            
            if passed:
                passed_count += 1
                
            res_log = EvaluationResultLog(
                run_id=run.id,
                case_id=case.case_id,
                passed=passed,
                metrics=metrics,
                actual_output=actual_output,
                error_message=err,
                latency_ms=latency
            )
            db.add(res_log)
        
        run.passed_cases = passed_count
        run.failed_cases = len(cases) - passed_count
        run.accuracy = (passed_count / len(cases)) * 100 if cases else 0.0
        run.status = "COMPLETED"
        run.completed_at = datetime.now(UTC)
        
        db.commit()
        db.refresh(run)
        return run

evaluation_engine = EvaluationEngine()
