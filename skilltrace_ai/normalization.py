"""
normalization.py: String cleaning, casing normalization, and canonical skill aliases.
"""

import re
from typing import Dict

# Canonical mapping for common variations in tech skill names
SKILL_ALIASES: Dict[str, str] = {
    "py": "python",
    "python3": "python",
    "js": "javascript",
    "ecmascript": "javascript",
    "ts": "typescript",
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "node": "node.js",
    "golang": "go",
    "postgres": "postgresql",
    "psql": "postgresql",
    "powerbi": "power bi",
    "power-bi": "power bi",
    "ms excel": "excel",
    "msexcel": "excel",
    "microsoft excel": "excel",
    "aws cloud": "aws",
    "amazon web services": "aws",
    "gcp": "google cloud",
    "k8s": "kubernetes",
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "fast-api": "fastapi",
}


def normalize_skill_name(name: str) -> str:
    """
    Normalizes a skill name by:
    1. Trimming leading and trailing whitespace
    2. Converting to lowercase
    3. Collapsing multiple spaces and hyphens where appropriate
    4. Mapping known aliases to their canonical standard
    """
    if not name or not isinstance(name, str):
        return ""

    cleaned = name.strip().lower()
    cleaned = re.sub(r"[\s_]+", " ", cleaned).strip()

    # Check alias dictionary
    return SKILL_ALIASES.get(cleaned, cleaned)
