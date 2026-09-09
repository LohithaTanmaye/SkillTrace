"""
recommender.py: Dynamic, personalized learning recommendations generated
directly from detected skill gaps with level-by-level milestones and hands-on projects.
"""

from typing import Any, Dict, List
from skilltrace_ai.normalization import normalize_skill_name

# Specific curriculum mappings and hands-on projects across levels
SKILL_CURRICULUM: Dict[str, Dict[str, Any]] = {
    "python": {
        "foundation": "Python syntax, data types, control flow, functions, lists, dicts, and file I/O.",
        "advanced": "OOP, generators, decorators, pytest unit testing, and modular packaging.",
        "milestones": [
            {
                "from_level": 1,
                "to_level": 2,
                "title": "Level 1 ➔ 2: Syntax & Fundamentals",
                "focus_topics": "Variables, loops (for/while), condition statements, functions, string manipulation.",
                "suggested_project": "Build a CLI Number Guessing Game or Task Tracker.",
            },
            {
                "from_level": 2,
                "to_level": 3,
                "title": "Level 2 ➔ 3: Core Data Structures & File I/O",
                "focus_topics": "Lists, dictionaries, sets, tuples, list comprehensions, reading/writing CSV & JSON.",
                "suggested_project": "Build a Contact Book application that persists data to CSV.",
            },
            {
                "from_level": 3,
                "to_level": 4,
                "title": "Level 3 ➔ 4: OOP & Modular Design",
                "focus_topics": "Classes, inheritance, exceptions, decorators, generators, unit testing with pytest.",
                "suggested_project": "Build an Object-Oriented Banking Simulation with full unit test coverage.",
            },
            {
                "from_level": 4,
                "to_level": 5,
                "title": "Level 4 ➔ 5: Concurrency & Performance",
                "focus_topics": "Asyncio, multiprocessing, memory profiling, type annotations, and design patterns.",
                "suggested_project": "Build an Async Web Scraper or High-Throughput Task Queue.",
            },
        ],
    },
    "sql": {
        "foundation": "SELECT queries, WHERE filtering, basic INNER/LEFT joins, and GROUP BY aggregations.",
        "advanced": "Multi-table joins, subqueries, CTEs, window functions (ROW_NUMBER/RANK), and indexing.",
        "milestones": [
            {
                "from_level": 1,
                "to_level": 2,
                "title": "Level 1 ➔ 2: Querying & Filtering",
                "focus_topics": "SELECT, WHERE, ORDER BY, DISTINCT, basic operators (LIKE, IN, BETWEEN).",
                "suggested_project": "Query a sample Ecommerce database to filter products and customers.",
            },
            {
                "from_level": 2,
                "to_level": 3,
                "title": "Level 2 ➔ 3: Joins & Aggregations",
                "focus_topics": "INNER JOIN, LEFT JOIN, GROUP BY, HAVING, aggregate functions (COUNT, SUM, AVG).",
                "suggested_project": "Generate a Monthly Sales Performance report calculating total revenues per category.",
            },
            {
                "from_level": 3,
                "to_level": 4,
                "title": "Level 3 ➔ 4: Subqueries & Window Functions",
                "focus_topics": "CTEs (WITH), correlated subqueries, ROW_NUMBER(), RANK(), DENSE_RANK(), LEAD/LAG.",
                "suggested_project": "Analyze Customer Churn and MoM Revenue growth using window functions.",
            },
            {
                "from_level": 4,
                "to_level": 5,
                "title": "Level 4 ➔ 5: Performance Tuning & Schema Design",
                "focus_topics": "B-Tree indexing, EXPLAIN query plans, partitioning, ACID transactions, and normalization.",
                "suggested_project": "Optimize a 1-million row query workload from 4.5s down to <50ms.",
            },
        ],
    },
    "power bi": {
        "foundation": "Data import, Power Query data cleaning, interactive dashboard design, and basic DAX.",
        "advanced": "Advanced DAX measures (CALCULATE/FILTER), star schema data modeling, and automated report publishing.",
        "milestones": [
            {
                "from_level": 1,
                "to_level": 2,
                "title": "Level 1 ➔ 2: Data Cleaning & Navigation",
                "focus_topics": "Power BI Desktop interface, loading Excel/CSV, Power Query transformations, basic charts.",
                "suggested_project": "Create a 1-page Sales Summary Dashboard with bar and line visuals.",
            },
            {
                "from_level": 2,
                "to_level": 3,
                "title": "Level 2 ➔ 3: Data Modeling & Measures",
                "focus_topics": "Relationships (1-to-many), calculated columns, DAX measures (SUM, AVERAGE, DIVIDE).",
                "suggested_project": "Build an HR Employee Retention dashboard with interactive slice filters.",
            },
            {
                "from_level": 3,
                "to_level": 4,
                "title": "Level 3 ➔ 4: Advanced DAX & Storytelling",
                "focus_topics": "CALCULATE, FILTER, ALL, Time Intelligence functions (YTD, MTD), bookmark drill-throughs.",
                "suggested_project": "Design an Executive Financial Performance cockpit with YoY variance analysis.",
            },
            {
                "from_level": 4,
                "to_level": 5,
                "title": "Level 4 ➔ 5: Enterprise Governance & Deployment",
                "focus_topics": "Row-Level Security (RLS), Gateway scheduled refreshes, composite models, performance analyzer.",
                "suggested_project": "Deploy a multi-department secured BI workspace with automated daily refresh.",
            },
        ],
    },
    "excel": {
        "foundation": "VLOOKUP/XLOOKUP, Pivot Tables, conditional formatting, and basic formulas.",
        "advanced": "Power Pivot, macro automation, data validation, and complex dashboard modeling.",
        "milestones": [
            {
                "from_level": 1,
                "to_level": 2,
                "title": "Level 1 ➔ 2: Essential Formulas & Formatting",
                "focus_topics": "SUM, AVERAGE, COUNT, basic IF, conditional formatting, basic charts.",
                "suggested_project": "Personal Monthly Expense & Budget Tracker.",
            },
            {
                "from_level": 2,
                "to_level": 3,
                "title": "Level 2 ➔ 3: Lookups & Pivot Tables",
                "focus_topics": "XLOOKUP, VLOOKUP, INDEX/MATCH, Pivot Tables, Pivot Charts, Slicers.",
                "suggested_project": "Inventory & Order Management dashboard.",
            },
            {
                "from_level": 3,
                "to_level": 4,
                "title": "Level 3 ➔ 4: Advanced Modeling & Automation",
                "focus_topics": "Nested logic, dynamic array formulas (FILTER, UNIQUE, SORT), Power Query in Excel.",
                "suggested_project": "Automated Financial Profit & Loss (P&L) model.",
            },
        ],
    },
    "fastapi": {
        "foundation": "REST API routing, path & query parameters, Pydantic request validation, and Swagger docs.",
        "advanced": "Dependency injection, async database sessions (SQLAlchemy), OAuth2 JWT security, and background tasks.",
        "milestones": [
            {
                "from_level": 1,
                "to_level": 2,
                "title": "Level 1 ➔ 2: Basic Endpoints & Pydantic",
                "focus_topics": "FastAPI instance, GET/POST routes, path parameters, query parameters, Pydantic BaseModel.",
                "suggested_project": "Build a Todo REST API with in-memory storage.",
            },
            {
                "from_level": 2,
                "to_level": 3,
                "title": "Level 2 ➔ 3: Database ORM & CRUD",
                "focus_topics": "SQLAlchemy 2.0 integration, database sessions, CRUD operations, error handling.",
                "suggested_project": "Build a Book Store API with SQLite database persistence.",
            },
            {
                "from_level": 3,
                "to_level": 4,
                "title": "Level 3 ➔ 4: Authentication & Architecture",
                "focus_topics": "OAuth2 JWT tokens, password hashing, dependency injection (Depends), async endpoints.",
                "suggested_project": "Build a Multi-User Blog API with role-based access control.",
            },
        ],
    },
    "docker": {
        "foundation": "Container concepts, Dockerfile creation, image building, and container execution.",
        "advanced": "Multi-stage builds, docker-compose orchestration, volume persistence, and networking.",
        "milestones": [
            {
                "from_level": 1,
                "to_level": 2,
                "title": "Level 1 ➔ 2: Docker Basics & Containers",
                "focus_topics": "docker run, docker ps, pulling images from Docker Hub, port mapping (-p).",
                "suggested_project": "Run an NGINX web server in a container with custom HTML.",
            },
            {
                "from_level": 2,
                "to_level": 3,
                "title": "Level 2 ➔ 3: Dockerfile & Custom Images",
                "focus_topics": "FROM, WORKDIR, COPY, RUN, CMD, building custom Python/Node images.",
                "suggested_project": "Containerize a FastAPI application with requirements.txt.",
            },
            {
                "from_level": 3,
                "to_level": 4,
                "title": "Level 3 ➔ 4: Docker Compose & Volumes",
                "focus_topics": "docker-compose.yml, multi-container orchestration, persistent volumes, bridge networks.",
                "suggested_project": "Run FastAPI + PostgreSQL + Redis stack via docker-compose.",
            },
        ],
    },
    "javascript": {
        "foundation": "ES6+ syntax, let/const scoping, array methods (map, filter, reduce), and DOM manipulation.",
        "advanced": "Async/await, promises, event loop, closures, fetch API integration, and error handling.",
        "milestones": [
            {
                "from_level": 1,
                "to_level": 2,
                "title": "Level 1 ➔ 2: Modern Syntax & DOM",
                "focus_topics": "let/const, arrow functions, template literals, document.querySelector, event listeners.",
                "suggested_project": "Interactive Calculator or Quiz UI in vanilla JS.",
            },
            {
                "from_level": 2,
                "to_level": 3,
                "title": "Level 2 ➔ 3: Arrays & Asynchronous JS",
                "focus_topics": "map(), filter(), reduce(), promises, fetch API, handling JSON.",
                "suggested_project": "Weather Dashboard that fetches data from a free public API.",
            },
            {
                "from_level": 3,
                "to_level": 4,
                "title": "Level 3 ➔ 4: Deep JS & Modular Architecture",
                "focus_topics": "Closures, prototypes, async/await, event bubbling, localStorage, error boundaries.",
                "suggested_project": "Full-featured Kanban Board with drag-and-drop and persistence.",
            },
        ],
    },
}


def get_level_milestones(skill_name: str, current_level: int, target_level: int) -> List[Dict[str, Any]]:
    """
    Returns step-by-step level progression milestones from current_level to target_level.
    """
    norm_key = normalize_skill_name(skill_name)
    curriculum = SKILL_CURRICULUM.get(norm_key, {})
    all_milestones = curriculum.get("milestones", [])

    filtered_milestones = []
    for m in all_milestones:
        # Include milestones between current_level and target_level
        if m["from_level"] >= max(1, current_level) and m["to_level"] <= target_level:
            filtered_milestones.append(m)

    # If no specific milestones found, provide intelligent generic roadmap
    if not filtered_milestones:
        for lvl in range(max(1, current_level), target_level):
            filtered_milestones.append({
                "from_level": lvl,
                "to_level": lvl + 1,
                "title": f"Level {lvl} ➔ {lvl + 1}: Step-by-Step Progression",
                "focus_topics": f"Focus on {skill_name} core competencies and applied exercises from Level {lvl} to Level {lvl + 1}.",
                "suggested_project": f"Build a practical {skill_name} portfolio project demonstrating Level {lvl + 1} concepts.",
            })

    return filtered_milestones


def generate_recommendations(prioritized_gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generates actionable learning recommendations tailored to each detected gap,
    complete with level-by-level milestone study steps and project ideas.
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

        # Generate step-by-step level roadmap
        milestones = get_level_milestones(name, stu_level, req_level)

        recommendations.append({
            "priority_rank": rank,
            "skill": name,
            "urgency": urgency,
            "current_level": stu_level,
            "target_level": req_level,
            "title": title,
            "action": action,
            "estimated_effort_weeks": max(1, (req_level - stu_level) * 2),
            "level_roadmap": milestones,
        })

    return recommendations
