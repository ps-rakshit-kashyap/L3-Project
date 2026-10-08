import argparse
import sys
from app.db.session import SessionLocal
from app.evaluation.engine import evaluation_engine

def main():
    parser = argparse.ArgumentParser(description="Run TalentForge Evaluations")
    parser.add_argument("--dataset", required=True, help="Path to JSON dataset")
    parser.add_argument("--agent", required=True, help="Agent/Task to evaluate")
    parser.add_argument("--model", default="mock", help="Model name")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        run = evaluation_engine.run_evaluation(db, args.dataset, args.agent, args.model)
        print(f"Evaluation Run Completed (ID: {run.id})")
        print(f"Cases: {run.total_cases}")
        print(f"Passed: {run.passed_cases}")
        print(f"Failed: {run.failed_cases}")
        print(f"Accuracy: {run.accuracy:.2f}%")
        
        if run.failed_cases > 0:
            print("\nFailed Cases:")
            for r in run.results:
                if not r.passed:
                    print(f" - {r.case_id}: {r.error_message or 'Metrics failed'}")
                    
        sys.exit(0 if run.failed_cases == 0 else 1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
