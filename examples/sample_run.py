"""
sample_run.py: Standalone demonstration of the skilltrace_ai engine.
Can be executed directly from command line to verify pure Python AI logic.
"""

import sys
from pathlib import Path
import json

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from skilltrace_ai import (
    analyze_assessment,
    assessment_to_student_skills,
    analyze_student,
)


def main():
    print("=" * 60)
    print("SKILLTRACE AI ENGINE DEMONSTRATION")
    print("=" * 60)

    # 1. Simulate student taking pre-assessment
    print("\n[Step 1] Simulating Pre-Assessment Submission...")
    assessment_input = {
        "assessment": [
            {"skill": "Python", "questions": 10, "correct_answers": 8},   # 80% -> Level 4
            {"skill": "SQL", "questions": 10, "correct_answers": 6},      # 60% -> Level 3
        ]
    }
    assessment_result = analyze_assessment(assessment_input)
    print(f"Evaluated Skills: {json.dumps(assessment_result['evaluated_skills'], indent=2)}")

    # 2. Convert assessment results into student profile skills
    print("\n[Step 2] Converting Assessment to Student Skills Profile...")
    student_skills = assessment_to_student_skills(assessment_result["evaluated_skills"])
    print(f"Student Profile: {json.dumps(student_skills, indent=2)}")

    # 3. Define target job benchmark
    target_job = {
        "job_title": "Junior Data Analyst",
        "job_skills": [
            {"name": "Python", "required_level": 4},
            {"name": "SQL", "required_level": 4},
            {"name": "Power BI", "required_level": 3},
        ],
    }

    # 4. Execute end-to-end skill matching and gap analysis
    print("\n[Step 3] Running AI Match & Skill-Gap Analysis...")
    analysis_payload = {
        "job_title": target_job["job_title"],
        "student_skills": student_skills,
        "job_skills": target_job["job_skills"],
    }
    analysis_result = analyze_student(analysis_payload)

    # 5. Display results
    print("\n" + "=" * 60)
    print(f"MATCH SCORE: {analysis_result['match_score']}%")
    print("=" * 60)
    print(f"\nMatched Skills ({len(analysis_result['matched_skills'])}):")
    for s in analysis_result["matched_skills"]:
        print(f"  - {s['name']}: Student Level {s['student_level']} / Required Level {s['required_level']}")

    print(f"\nPartial Gaps ({len(analysis_result['partial_gaps'])}):")
    for s in analysis_result["partial_gaps"]:
        print(f"  - {s['name']}: Student Level {s['student_level']} / Required Level {s['required_level']} (Deficit: {s['deficit']})")

    print(f"\nMissing Skills ({len(analysis_result['missing_skills'])}):")
    for s in analysis_result["missing_skills"]:
        print(f"  - {s['name']}: Required Level {s['required_level']} (Completely Missing)")

    print("\nTop Prioritized Recommendations:")
    for r in analysis_result["recommendations"]:
        print(f"  [{r['urgency']}] #{r['priority_rank']} {r['skill']}: {r['action']}")

    print("\nNatural Language Explanation:")
    print(f"  \"{analysis_result['explanation']}\"")

    print("\nMandatory Ethical Disclaimer:")
    print(f"  \"{analysis_result['disclaimer']}\"")
    print("=" * 60)


if __name__ == "__main__":
    main()
