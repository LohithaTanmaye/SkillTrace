# SKILLTRACE 🎯

> **Student Skill Analysis & Job-Readiness Platform**  
> *Smart India Hackathon (SIH) 2026*

---

## 📌 Overview

**SKILLTRACE** is an explainable AI-powered skill analysis and job-readiness platform. It bridges the gap between student competencies and industry hiring standards through transparent, auditable skill evaluation.

### Key Capabilities
- **Pre-Assessment Engine**: Skill-specific question assessment with strict 5-level proficiency mapping.
- **Explainable Matching Algorithm**: Deterministic normalized matching with optional semantic similarity.
- **3-Tier Skill Gap Analysis**: Full Match, Partial Gap, and Missing Skills.
- **Auditable Match Score**: Transparent mathematical formula without black-box scoring.
- **Targeted Recommendations**: Dynamic learning roadmaps generated specifically for detected deficits.
- **Ethical AI Disclaimer**: Clear communication of score as an alignment estimate, avoiding false employment guarantees.

---

## 📐 Interpretable Scoring Formula

For each skill required by a target job:

$$\text{skill\_score} = \min\left(\frac{\text{student\_level}}{\text{required\_level}}, 1.0\right)$$

Overall Job Match Score:

$$\text{match\_score} = \text{round}\left(\frac{\sum \text{skill\_score}}{N} \times 100, 1\right)$$

*Example:*  
- Python: Student Level 4 / Required Level 4 $\rightarrow$ Score: 1.0  
- SQL: Student Level 3 / Required Level 4 $\rightarrow$ Score: 0.75  
- Power BI: Student Level 0 / Required Level 3 $\rightarrow$ Score: 0.0  
**Overall Match Score:** $\frac{1.0 + 0.75 + 0.0}{3} \times 100 = 58.3\%$

---

## 📁 Project Structure

```text
SKILLTRACE/
├── backend/          # FastAPI routes, schemas, models & services
├── skilltrace_ai/    # Pure standalone AI engine (Matching, Gaps, Scorer, Explainer)
├── data/             # Benchmark CSV datasets (jobs, students, assessments)
├── frontend/         # Interactive responsive HTML/CSS/JS dashboard
├── tests/            # Automated Pytest boundary & integration tests
├── examples/         # Sample scripts & demonstration payloads
├── requirements.txt  # Python package dependencies
├── pyproject.toml    # Project metadata & test configuration
└── README.md         # Documentation
```

---

## 🚀 Quickstart

### 1. Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run Test Suite
```powershell
python -m pytest tests/ -v
```

### 4. Start FastAPI Server
```powershell
uvicorn backend.main:app --reload
```
API Documentation will be live at: `http://127.0.0.1:8000/docs`

---

## ⚖️ Disclaimer
*The match score provided by SKILLTRACE is an estimate of skill alignment based on available assessment data and stated job requirements. It does not guarantee employment or job suitability.*
