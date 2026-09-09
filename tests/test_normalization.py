"""
test_normalization.py: Unit tests for string cleaning and canonical skill aliases.
"""

from skilltrace_ai.normalization import normalize_skill_name, SKILL_ALIASES


def test_normalize_whitespace_and_casing():
    assert normalize_skill_name("  Python  ") == "python"
    assert normalize_skill_name("PYTHON") == "python"
    assert normalize_skill_name("  pyThOn   ") == "python"
    assert normalize_skill_name("Power   BI") == "power bi"


def test_normalize_aliases():
    assert normalize_skill_name("py") == "python"
    assert normalize_skill_name("python3") == "python"
    assert normalize_skill_name("js") == "javascript"
    assert normalize_skill_name("reactjs") == "react"
    assert normalize_skill_name("react.js") == "react"
    assert normalize_skill_name("nodejs") == "node.js"
    assert normalize_skill_name("postgres") == "postgresql"
    assert normalize_skill_name("powerbi") == "power bi"
    assert normalize_skill_name("ms excel") == "excel"
    assert normalize_skill_name("sklearn") == "scikit-learn"
    assert normalize_skill_name("fast-api") == "fastapi"


def test_normalize_edge_cases():
    assert normalize_skill_name("") == ""
    assert normalize_skill_name("   ") == ""
    assert normalize_skill_name(None) == ""
    assert normalize_skill_name(12345) == ""
