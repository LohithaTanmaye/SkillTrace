"""
recommender.py: Dynamic, personalized learning recommendations generated
directly from detected skill gaps.
"""

from typing import Any, Dict, List
from skilltrace_ai.normalization import normalize_skill_name

# Specific topic curriculum mappings across beginner (Levels 1-2) and advanced (Levels 3-5)
SKILL_CURRICULUM: Dict[str, Dict[str, str]] = {
    "python": {
        "foundation": "Python syntax, control flow, functions, lists, dictionaries, and file I/O.",
        "advanced": "OOP, generators, decorators, pytest unit testing, and modular architecture.",
    },
    "sql": {
        "foundation": "SELECT queries, WHERE filtering, basic INNER/LEFT joins, and GROUP BY aggregations.",
        "advanced": "Multi-table joins, subqueries, CTEs, window functions (ROW_NUMBER/RANK), and index optimization.",
    },
    "power bi": {
        "foundation": "Data import, Power Query data cleaning, interactive dashboard design, and basic DAX.",
        "advanced": "Advanced DAX measures (CALCULATE/FILTER), star schema data modeling, and automated report publishing.",
    },
    "excel": {
        "foundation": "VLOOKUP/XLOOKUP, Pivot Tables, conditional formatting, and basic formulas (SUMIFS/COUNTIFS).",
        "advanced": "Power Pivot, macro automation, data validation, and complex dashboard modeling.",
    },
    "javascript": {
        "foundation": "ES6+ syntax, let/const scoping, array methods (map, filter, reduce), and DOM manipulation.",
        "advanced": "Async/await, promises, event loop, closures, fetch API integration, and error handling.",
    },
    "react": {
        "foundation": "Functional components, JSX syntax, props, useState, and component event handling.",
        "advanced": "Custom hooks, useEffect lifecycle management, Context API state sharing, and memoization.",
    },
    "fastapi": {
        "foundation": "REST API routing, path & query parameters, Pydantic request validation, and Swagger docs.",
        "advanced": "Dependency injection, async database sessions (SQLAlchemy), OAuth2 JWT security, and background tasks.",
    },
    "docker": {
        "foundation": "Container concepts, Dockerfile creation, image building, and container execution.",
        "advanced": "Multi-stage builds, docker-compose orchestration, volume persistence, and networking.",
    },
    "git": {
        "foundation": "Version control fundamentals: git init, add, commit, push, pull, and branch creation.",
        "advanced": "Resolving merge conflicts, interactive rebasing, Git workflows (PRs), and cherry-picking.",
    },
    "machine learning": {
        "foundation": "Supervised learning workflows, train/test splitting, linear regression, and classification.",
        "advanced": "Cross-validation, hyperparameter tuning, ensemble methods (Random Forest, XGBoost), and scikit-learn pipelines.",
    },
    "statistics": {
        "foundation": "Descriptive statistics, mean/median/mode, variance, standard deviation, and normal distribution.",
        "advanced": "Hypothesis testing, p-values, confidence intervals, A/B testing, and correlation vs causation.",
    },
    "linux": {
        "foundation": "Bash navigation (cd, ls, mkdir), file permissions (chmod, chown), and text inspection (grep, cat).",
        "advanced": "Shell scripting, process management (systemd, ps, top), SSH key authentication, and cron jobs.",
    },
    "aws": {
        "foundation": "Cloud basics, IAM user permissions, S3 bucket storage, and EC2 instance provisioning.",
        "advanced": "VPC networking, Lambda serverless functions, RDS database setup, and CloudWatch monitoring.",
    },
}


def generate_recommendations(prioritized_gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generates actionable learning recommendations tailored to each detected gap.
    Does not output generic one-size-fits-all text.
    """
    recommendations = []

    for gap in prioritized_gaps:
        name = gap.get("name", "Unknown")
        stu_level = gap.get("student_level", 0)
        req_level = gap.get("required_level", 1)
        urgency = gap.get("urgency", "MEDIUM")
        rank = gap.get("rank", 1)

        norm_key = normalize_skill_name(name)
        curriculum = SKILL_CURRICULUM.get(norm_key, {})

        if stu_level == 0:
            # Completely missing skill
            focus_topics = curriculum.get(
                "foundation",
                f"{name} fundamentals, core concepts, and beginner hands-on mini-projects."
            )
            title = f"Start Learning {name} Fundamentals"
            action = (
                f"Start learning {name} fundamentals to reach Level {req_level}. "
                f"Focus on: {focus_topics}"
            )
        else:
            # Partial skill gap
            if stu_level <= 2:
                focus_topics = curriculum.get(
                    "foundation",
                    f"core practical patterns, intermediate syntax, and applied exercises."
                )
            else:
                focus_topics = curriculum.get(
                    "advanced",
                    f"advanced architectural patterns, optimization, and production best practices."
                )

            title = f"Advance {name} from Level {stu_level} to Level {req_level}"
            action = (
                f"Improve {name} from Level {stu_level} toward required Level {req_level}. "
                f"Focus on: {focus_topics}"
            )

        recommendations.append({
            "priority_rank": rank,
            "skill": name,
            "urgency": urgency,
            "current_level": stu_level,
            "target_level": req_level,
            "title": title,
            "action": action,
            "estimated_effort_weeks": max(1, (req_level - stu_level) * 2),
        })

    return recommendations
