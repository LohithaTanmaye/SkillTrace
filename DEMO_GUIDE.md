# 🎯 SKILLTRACE: Hackathon Judge Demo Script (SIH 2026)

---

## ⏱️ 1. Opening Pitch (30-45 Seconds)

> *"Good morning, respected judges. Current job portals give students an opaque percentage match or reject their resumes without explaining why. Students are left asking: 'What skills am I missing? How far off am I? What should I study first?'*
> 
> *We built **SKILLTRACE** — an explainable student skill analysis and job-readiness platform. It objectively estimates proficiency through pre-assessments, categorizes gaps across three distinct tiers, computes an auditable mathematical match score, and generates a personalized, prioritized learning roadmap."*

---

## 🎬 2. Live Demo Flow (3 Minutes)

### Step 1: Start the Platform
In PowerShell or Terminal:
```powershell
.\run_demo.ps1
```
Open browser to: **`http://127.0.0.1:8000`**

---

### Step 2: Show the Pre-Assessment (`/assessment.html`)
1. Click **"Take Pre-Assessment"**.
2. Point out to judges:
   - Target Job selection (e.g. **Junior Data Analyst**).
   - Calibrated questions fetched dynamically from our database/CSV question bank.
   - Questions evaluate core competencies (Python, SQL, Power BI, Git, Docker).
3. Select answers:
   - Python Q1: **C (Tuple)**
   - Python Q2: **B (yield)**
   - SQL Q1: **B (HAVING)**
4. Click **"Submit & View Job Readiness"**.

---

### Step 3: Walk Through the Results Page (`/results.html`)
Walk the judges through the UI sections from top to bottom:

1. **Overall Match Score Badge**:
   - Shows the calculated alignment percentage.
2. **Explainable AI Summary**:
   - Reads a clear paragraph explaining strengths, partial deficits, and missing prerequisites.
3. **3-Tier Gap Analysis Cards**:
   - 🟢 **Matched Skills**: Requirements met or exceeded (e.g., Python Level 4 / 4).
   - 🟡 **Partial Gaps**: Student has the skill, but is below expected level (e.g., SQL Level 3 / 4, Deficit -1).
   - 🔴 **Missing Skills**: Prerequisite completely absent (e.g., Power BI Level 0 / 3).
4. **Prioritized Action Plan**:
   - Point out the **HIGH / MEDIUM / LOW** urgency badges.
   - Note that recommendations are **context-aware**: they specify exact topics (e.g. for Power BI: *"data import, Power Query data cleaning, basic DAX"*).
5. **Mathematical Score Audit**:
   - Open the calculation table: Show judges the formula:
     $$\text{skill\_score} = \min\left(\frac{\text{student\_level}}{\text{required\_level}}, 1.0\right)$$
   - Point out: *"Every single number is auditable. There is zero hallucination or black-box guessing."*
6. **Ethical AI Disclaimer**:
   - Point out the mandatory disclaimer: *"The score is an alignment estimate; we do not make false promises or guarantee employment."*

---

### Step 4: Show the Interactive Matcher (`/dashboard.html`)
1. Click **"Skill Matcher"** in the top navigation bar.
2. Select the **Rahul Sharma** persona preset (Python: 4, SQL: 3, Excel: 4).
3. Target Job: **Junior Data Analyst** (Python: 4, SQL: 4, Power BI: 3).
4. Click **"Analyze Job Readiness"**.
5. Show how the exact score **58.3%** is computed in real time:
   $$\frac{1.0 + 0.75 + 0.0}{3} \times 100 = 58.3\%$$

---

### Step 5: Backend & Testing Verification (`/docs` & Pytest)
1. Open **`http://127.0.0.1:8000/docs`** to show FastAPI's interactive Swagger documentation.
2. Run automated test suite in terminal:
   ```powershell
   python -m pytest tests/ -v
   ```
   Highlight: **45 automated tests** covering boundary conditions (20%, 40%, 60%, 80%, 100%), error handling, and API integration.
