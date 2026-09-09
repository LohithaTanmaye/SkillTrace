/**
 * script.js: Central JavaScript engine for SKILLTRACE frontend.
 * Manages API calls, student registration modal, multi-role career matching,
 * level study roadmaps, and dashboard rendering.
 */

const API_BASE = window.location.origin.includes(":8000") 
  ? window.location.origin 
  : "http://127.0.0.1:8000";

// Generic API caller
async function apiCall(endpoint, method = "GET", body = null) {
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };
  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Network request failed" }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

// State Persistence
function setAnalysisResult(data) {
  localStorage.setItem("skilltrace_analysis", JSON.stringify(data));
}

function getAnalysisResult() {
  const data = localStorage.getItem("skilltrace_analysis");
  return data ? JSON.parse(data) : null;
}

function setMultiRoleResult(data) {
  localStorage.setItem("skilltrace_multi_roles", JSON.stringify(data));
}

function getMultiRoleResult() {
  const data = localStorage.getItem("skilltrace_multi_roles");
  return data ? JSON.parse(data) : null;
}

function setStudentSkills(skills) {
  localStorage.setItem("skilltrace_student_skills", JSON.stringify(skills));
}

function getStudentSkills() {
  const data = localStorage.getItem("skilltrace_student_skills");
  return data ? JSON.parse(data) : null;
}

// -------------------------------------------------------------
// ASSESSMENT PAGE LOGIC
// -------------------------------------------------------------
async function initAssessmentPage() {
  const container = document.getElementById("questions-container");
  const jobSelect = document.getElementById("target-job-select");
  const form = document.getElementById("assessment-form");
  if (!container || !form) return;

  try {
    const [questions, jobs] = await Promise.all([
      apiCall("/assessment/questions"),
      apiCall("/jobs"),
    ]);

    if (jobSelect) {
      jobSelect.innerHTML = jobs.map(j => 
        `<option value="${j.job_id}">${j.title} (${j.domain})</option>`
      ).join("");
    }

    container.innerHTML = questions.map((q, idx) => `
      <div class="question-item" data-qid="${q.question_id}">
        <div class="question-title">
          <span class="badge badge-neutral">${q.skill}</span>
          ${idx + 1}. ${q.question_text}
        </div>
        <div class="options-group">
          ${Object.entries(q.options).map(([optKey, optVal]) => `
            <label class="option-label">
              <input type="radio" name="q_${q.question_id}" value="${optKey}" required>
              <strong>${optKey}:</strong> ${optVal}
            </label>
          `).join("")}
        </div>
      </div>
    `).join("");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitBtn = form.querySelector("button[type='submit']");
      submitBtn.disabled = true;
      submitBtn.innerText = "Evaluating Assessment...";

      const answers = [];
      questions.forEach(q => {
        const selected = form.querySelector(`input[name="q_${q.question_id}"]:checked`);
        if (selected) {
          answers.push({
            question_id: q.question_id,
            selected_option: selected.value,
          });
        }
      });

      try {
        const payload = {
          answers,
          target_job_id: jobSelect ? jobSelect.value : "JOB001",
        };

        const result = await apiCall("/assessment/submit", "POST", payload);

        setStudentSkills(result.student_skills_profile);
        if (result.job_analysis) {
          setAnalysisResult(result.job_analysis);
          // Also fetch all role recommendations in background
          try {
            const allRoles = await apiCall("/analyze/all-roles", "POST", result.student_skills_profile);
            setMultiRoleResult(allRoles);
          } catch (err) {}
          window.location.href = "results.html";
        } else {
          window.location.href = "dashboard.html";
        }
      } catch (err) {
        alert(`Assessment Submission Error: ${err.message}`);
        submitBtn.disabled = false;
        submitBtn.innerText = "Submit & View Job Readiness";
      }
    });
  } catch (err) {
    container.innerHTML = `<div class="disclaimer-box" style="color: var(--danger)">Failed to load questions. Verify backend is running.</div>`;
  }
}

// -------------------------------------------------------------
// DASHBOARD / JOB MATCHER PAGE LOGIC
// -------------------------------------------------------------
async function initDashboardPage() {
  const presetSelect = document.getElementById("student-preset");
  const jobSelect = document.getElementById("job-select");
  const skillsList = document.getElementById("skills-list");
  const addSkillBtn = document.getElementById("add-skill-btn");
  const analyzeBtn = document.getElementById("analyze-btn");
  const exploreRolesBtn = document.getElementById("explore-all-roles-btn");

  // Modal elements
  const openModalBtn = document.getElementById("open-register-modal-btn");
  const closeModalBtn = document.getElementById("close-modal-btn");
  const cancelModalBtn = document.getElementById("cancel-modal-btn");
  const modalBackdrop = document.getElementById("register-modal");
  const registerForm = document.getElementById("register-student-form");
  const modalSkillsList = document.getElementById("modal-skills-list");
  const modalAddSkillBtn = document.getElementById("modal-add-skill-btn");

  if (!skillsList || !analyzeBtn) return;

  try {
    const [students, jobs] = await Promise.all([
      apiCall("/students"),
      apiCall("/jobs"),
    ]);

    // Populate jobs
    if (jobSelect) {
      jobSelect.innerHTML = jobs.map(j => `
        <option value="${j.job_id}" data-skills='${JSON.stringify(j.job_skills)}'>
          ${j.title} (${j.domain})
        </option>
      `).join("");
    }

    // Populate student presets
    function populateStudentPresets(allStudents, selectedId = "") {
      if (!presetSelect) return;
      presetSelect.innerHTML = `<option value="">-- Custom Profile --</option>` +
        allStudents.map(s => `
          <option value="${s.student_id}" data-skills='${JSON.stringify(s.student_skills)}' ${s.student_id === selectedId ? "selected" : ""}>
            ${s.name} (${s.student_skills.map(sk => sk.name).join(", ")})
          </option>
        `).join("");
    }

    populateStudentPresets(students);

    presetSelect.addEventListener("change", () => {
      const selected = presetSelect.options[presetSelect.selectedIndex];
      if (selected.dataset.skills) {
        renderSkillRows(JSON.parse(selected.dataset.skills));
      }
    });

    // Render initial skills
    const cached = getStudentSkills();
    if (cached && cached.length > 0) {
      renderSkillRows(cached);
    } else {
      renderSkillRows([
        { name: "Python", level: 4 },
        { name: "SQL", level: 3 },
        { name: "Excel", level: 4 },
      ]);
    }

    addSkillBtn.addEventListener("click", () => {
      addSkillRow("", 3);
    });

    // Run Single Job Analysis
    analyzeBtn.addEventListener("click", async () => {
      const studentSkills = collectSkillsFromUI();
      if (studentSkills.length === 0) {
        alert("Please add at least one skill to your profile.");
        return;
      }

      const selectedJobOption = jobSelect.options[jobSelect.selectedIndex];
      const jobSkills = JSON.parse(selectedJobOption.dataset.skills);
      const jobTitle = selectedJobOption.text.split(" (")[0];

      analyzeBtn.disabled = true;
      analyzeBtn.innerText = "Analyzing Readiness...";

      try {
        const payload = {
          job_title: jobTitle,
          student_skills: studentSkills,
          job_skills: jobSkills,
        };

        const [analysis, multiRoles] = await Promise.all([
          apiCall("/analyze", "POST", payload),
          apiCall("/analyze/all-roles", "POST", studentSkills).catch(() => null),
        ]);

        setAnalysisResult(analysis);
        if (multiRoles) setMultiRoleResult(multiRoles);
        setStudentSkills(studentSkills);
        window.location.href = "results.html";
      } catch (err) {
        alert(`Analysis Error: ${err.message}`);
        analyzeBtn.disabled = false;
        analyzeBtn.innerText = "Analyze Selected Job Readiness ➔";
      }
    });

    // Explore All Roles Button
    if (exploreRolesBtn) {
      exploreRolesBtn.addEventListener("click", async () => {
        const studentSkills = collectSkillsFromUI();
        if (studentSkills.length === 0) {
          alert("Please add at least one skill to check eligible roles.");
          return;
        }

        exploreRolesBtn.disabled = true;
        exploreRolesBtn.innerText = "Searching Compatible Roles...";

        try {
          const selectedJobOption = jobSelect.options[jobSelect.selectedIndex];
          const jobSkills = JSON.parse(selectedJobOption.dataset.skills);
          const jobTitle = selectedJobOption.text.split(" (")[0];

          const [analysis, multiRoles] = await Promise.all([
            apiCall("/analyze", "POST", { job_title: jobTitle, student_skills: studentSkills, job_skills: jobSkills }),
            apiCall("/analyze/all-roles", "POST", studentSkills),
          ]);

          setAnalysisResult(analysis);
          setMultiRoleResult(multiRoles);
          setStudentSkills(studentSkills);
          window.location.href = "results.html";
        } catch (err) {
          alert(`Error fetching roles: ${err.message}`);
          exploreRolesBtn.disabled = false;
          exploreRolesBtn.innerText = "🔍 Explore All Eligible Job Roles (Career Fit)";
        }
      });
    }

    // Modal Handlers
    function openModal() {
      modalBackdrop.classList.add("active");
      modalSkillsList.innerHTML = "";
      addModalSkillRow("Python", 4);
      addModalSkillRow("SQL", 3);
    }
    function closeModal() {
      modalBackdrop.classList.remove("active");
    }

    if (openModalBtn) openModalBtn.addEventListener("click", openModal);
    if (closeModalBtn) closeModalBtn.addEventListener("click", closeModal);
    if (cancelModalBtn) cancelModalBtn.addEventListener("click", closeModal);

    function addModalSkillRow(name = "", level = 3) {
      const row = document.createElement("div");
      row.className = "gap-item";
      row.style.padding = "0.3rem 0";
      row.innerHTML = `
        <input type="text" class="m-skill-name" value="${name}" placeholder="Skill" style="padding: 0.35rem 0.5rem; width: 60%; border: 1px solid var(--border); border-radius: var(--radius-sm);">
        <select class="m-skill-level" style="padding: 0.35rem; border: 1px solid var(--border); border-radius: var(--radius-sm);">
          <option value="1" ${level === 1 ? "selected" : ""}>1</option>
          <option value="2" ${level === 2 ? "selected" : ""}>2</option>
          <option value="3" ${level === 3 ? "selected" : ""}>3</option>
          <option value="4" ${level === 4 ? "selected" : ""}>4</option>
          <option value="5" ${level === 5 ? "selected" : ""}>5</option>
        </select>
        <button type="button" class="btn btn-secondary m-del-btn" style="padding: 0.2rem 0.5rem; color: var(--danger);">✕</button>
      `;
      row.querySelector(".m-del-btn").addEventListener("click", () => row.remove());
      modalSkillsList.appendChild(row);
    }

    if (modalAddSkillBtn) {
      modalAddSkillBtn.addEventListener("click", () => addModalSkillRow("", 3));
    }

    if (registerForm) {
      registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("new-student-name").value.trim();
        const email = document.getElementById("new-student-email").value.trim();
        const degree = document.getElementById("new-student-degree").value.trim();

        const skillRows = modalSkillsList.querySelectorAll(".gap-item");
        const student_skills = [];
        skillRows.forEach(r => {
          const sName = r.querySelector(".m-skill-name").value.trim();
          const sLvl = parseInt(r.querySelector(".m-skill-level").value, 10);
          if (sName) student_skills.push({ name: sName, level: sLvl });
        });

        if (student_skills.length === 0) {
          alert("Please specify at least one skill for the new student.");
          return;
        }

        const submitBtn = registerForm.querySelector("button[type='submit']");
        submitBtn.disabled = true;
        submitBtn.innerText = "Saving Profile...";

        try {
          const created = await apiCall("/students", "POST", {
            name,
            email,
            degree,
            student_skills,
          });

          // Reload all students
          const updatedStudents = await apiCall("/students");
          populateStudentPresets(updatedStudents, created.student_id);
          renderSkillRows(created.student_skills);
          setStudentSkills(created.student_skills);

          alert(`Success! Student '${name}' registered as ${created.student_id}.`);
          closeModal();
          registerForm.reset();
        } catch (err) {
          alert(`Registration Error: ${err.message}`);
        } finally {
          submitBtn.disabled = false;
          submitBtn.innerText = "Save & Load Profile";
        }
      });
    }

  } catch (err) {
    console.error("Dashboard error:", err);
  }

  function renderSkillRows(skills) {
    skillsList.innerHTML = "";
    skills.forEach(s => addSkillRow(s.name, s.level));
  }

  function addSkillRow(name = "", level = 3) {
    const row = document.createElement("div");
    row.className = "gap-item";
    row.innerHTML = `
      <input type="text" class="skill-name-input" value="${name}" placeholder="e.g. Python" style="padding: 0.4rem 0.6rem; border: 1px solid var(--border); border-radius: var(--radius-sm); width: 60%; font-weight: 600;">
      <div style="display: flex; align-items: center; gap: 0.5rem;">
        <span style="font-size: 0.85rem; color: var(--text-muted);">Level:</span>
        <select class="skill-level-select" style="padding: 0.4rem; border: 1px solid var(--border); border-radius: var(--radius-sm); font-weight: 600;">
          <option value="1" ${level === 1 ? "selected" : ""}>1 (Beginner)</option>
          <option value="2" ${level === 2 ? "selected" : ""}>2 (Basic)</option>
          <option value="3" ${level === 3 ? "selected" : ""}>3 (Intermediate)</option>
          <option value="4" ${level === 4 ? "selected" : ""}>4 (Advanced)</option>
          <option value="5" ${level === 5 ? "selected" : ""}>5 (Proficient)</option>
        </select>
        <button type="button" class="btn btn-secondary delete-skill-btn" style="padding: 0.3rem 0.6rem; color: var(--danger);">✕</button>
      </div>
    `;

    row.querySelector(".delete-skill-btn").addEventListener("click", () => row.remove());
    skillsList.appendChild(row);
  }

  function collectSkillsFromUI() {
    const rows = skillsList.querySelectorAll(".gap-item");
    const list = [];
    rows.forEach(r => {
      const name = r.querySelector(".skill-name-input").value.trim();
      const level = parseInt(r.querySelector(".skill-level-select").value, 10);
      if (name) {
        list.push({ name, level });
      }
    });
    return list;
  }
}

// -------------------------------------------------------------
// RESULTS PAGE LOGIC (with Multi-Role Match & Level Roadmaps)
// -------------------------------------------------------------
function initResultsPage() {
  const result = getAnalysisResult();
  const multiRoles = getMultiRoleResult();
  const container = document.getElementById("results-content");
  if (!container) return;

  if (!result) {
    container.innerHTML = `
      <div class="card" style="text-align: center; padding: 3rem;">
        <h2>No Analysis Found</h2>
        <p style="color: var(--text-muted); margin: 1rem 0;">Please take the pre-assessment or run a match from the dashboard.</p>
        <a href="dashboard.html" class="btn btn-primary">Go to Dashboard</a>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <!-- Top Score Banner -->
    <div class="score-banner">
      <div>
        <div class="score-label">OVERALL SKILL ALIGNMENT ESTIMATE</div>
        <div class="score-number">${result.match_score}%</div>
        <div style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">
          Computed across ${result.score_breakdown ? result.score_breakdown.length : 0} required skills
        </div>
      </div>
      <div style="text-align: right;">
        <span class="badge ${result.match_score >= 75 ? 'badge-success' : (result.match_score >= 45 ? 'badge-warning' : 'badge-danger')}" style="font-size: 1rem; padding: 0.5rem 1rem;">
          ${result.match_score >= 75 ? 'Strong Alignment' : (result.match_score >= 45 ? 'Moderate Alignment' : 'Foundational Readiness')}
        </span>
      </div>
    </div>

    <!-- Multi-Role Career Recommendations Leaderboard -->
    ${multiRoles && multiRoles.ranked_roles ? `
      <div class="card">
        <div class="card-header">
          <h3>💼 Career Roles You Can Target ("Inka Em Em Roles ki Apply Cheyochu")</h3>
          <span class="badge badge-neutral">${multiRoles.total_roles_evaluated} Benchmark Roles Analyzed</span>
        </div>
        <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1rem;">
          Based on your current competencies, here is how well you match across different industry career paths:
        </p>
        <div>
          ${multiRoles.ranked_roles.map(r => `
            <div class="role-fit-card ${r.fit_tier === 'Ready to Apply' ? 'fit-ready' : (r.fit_tier === 'Close Match' ? 'fit-close' : 'fit-future')}">
              <div>
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                  <strong style="font-size: 1.05rem; color: var(--secondary);">${r.title}</strong>
                  <span class="badge ${r.fit_tier === 'Ready to Apply' ? 'badge-success' : (r.fit_tier === 'Close Match' ? 'badge-warning' : 'badge-neutral')}">
                    ${r.fit_tier}
                  </span>
                </div>
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem;">
                  Domain: <strong>${r.domain}</strong> | Exp: ${r.experience_level}
                </div>
                <div style="font-size: 0.8rem; margin-top: 0.35rem;">
                  <span style="color: var(--success); font-weight: 600;">✓ Matched:</span> ${r.matched_skill_names.join(", ") || "None"}
                  ${r.top_missing_skills.length > 0 ? `<span style="color: var(--danger); margin-left: 0.75rem; font-weight: 600;">✕ Deficit:</span> ${r.top_missing_skills.join(", ")}` : ""}
                </div>
              </div>
              <div style="text-align: right; min-width: 90px;">
                <div style="font-size: 1.75rem; font-weight: 800; color: ${r.match_score >= 70 ? 'var(--success)' : (r.match_score >= 45 ? '#b45309' : 'var(--text-muted)')};">
                  ${r.match_score}%
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted);">Alignment</div>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    ` : ''}

    <!-- Explainable Summary -->
    <div class="card">
      <div class="card-header">
        <h3>🔍 Explainable AI Summary</h3>
      </div>
      <p style="font-size: 1.05rem; line-height: 1.6; color: var(--secondary);">
        ${result.explanation}
      </p>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.75rem;">
        <strong>Scoring Mechanics:</strong> ${result.explanation_details ? result.explanation_details.score_explanation : ''}
      </p>
    </div>

    <!-- 3-Tier Gap Analysis Grid -->
    <div class="grid-3">
      <!-- Matched Skills -->
      <div class="card">
        <div class="card-header">
          <h3 style="color: var(--success);">🟢 Matched Skills (${result.matched_skills.length})</h3>
        </div>
        ${result.matched_skills.length === 0 ? '<p style="color: var(--text-muted); font-size: 0.9rem;">None meeting requirement.</p>' : ''}
        ${result.matched_skills.map(s => `
          <div class="gap-item">
            <strong>${s.name}</strong>
            <span class="badge badge-success">Level ${s.student_level} / ${s.required_level}</span>
          </div>
        `).join("")}
      </div>

      <!-- Partial Gaps -->
      <div class="card">
        <div class="card-header">
          <h3 style="color: #b45309;">🟡 Partial Gaps (${result.partial_gaps.length})</h3>
        </div>
        ${result.partial_gaps.length === 0 ? '<p style="color: var(--text-muted); font-size: 0.9rem;">No partial deficits.</p>' : ''}
        ${result.partial_gaps.map(s => `
          <div class="gap-item">
            <div>
              <strong>${s.name}</strong>
              <div style="font-size: 0.75rem; color: var(--text-muted);">Deficit: -${s.deficit} Level(s)</div>
            </div>
            <span class="badge badge-warning">Lvl ${s.student_level} ➔ ${s.required_level}</span>
          </div>
        `).join("")}
      </div>

      <!-- Missing Skills -->
      <div class="card">
        <div class="card-header">
          <h3 style="color: var(--danger);">🔴 Missing Skills (${result.missing_skills.length})</h3>
        </div>
        ${result.missing_skills.length === 0 ? '<p style="color: var(--text-muted); font-size: 0.9rem;">No missing prerequisites.</p>' : ''}
        ${result.missing_skills.map(s => `
          <div class="gap-item">
            <strong>${s.name}</strong>
            <span class="badge badge-danger">Req: Level ${s.required_level}</span>
          </div>
        `).join("")}
      </div>
    </div>

    <!-- Targeted Recommendations & Level-by-Level Study Roadmap -->
    <div class="card">
      <div class="card-header">
        <h3>📚 Level-by-Level Learning Roadmap & Projects</h3>
      </div>
      <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1.25rem;">
        Detailed milestones guiding exactly what topics to study at each proficiency tier and portfolio project suggestions:
      </p>

      ${result.recommendations.map(r => `
        <div class="rec-card" style="margin-bottom: 1.5rem;">
          <div class="rec-title">
            <span>#${r.priority_rank} ${r.title}</span>
            <span class="badge ${r.urgency === 'HIGH' ? 'badge-danger' : (r.urgency === 'MEDIUM' ? 'badge-warning' : 'badge-neutral')}">
              ${r.urgency} PRIORITY
            </span>
          </div>
          <div class="rec-action" style="margin-bottom: 0.75rem;">${r.action}</div>

          <!-- Step-by-Step Milestones Timeline -->
          ${r.level_roadmap && r.level_roadmap.length > 0 ? `
            <div style="background: #ffffff; border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1rem; margin-top: 0.75rem;">
              <div style="font-size: 0.85rem; font-weight: 700; color: var(--secondary); margin-bottom: 0.75rem;">
                🎯 Step-by-Step Progression Milestones:
              </div>
              ${r.level_roadmap.map(m => `
                <div class="roadmap-step">
                  <div class="roadmap-bullet"></div>
                  <div style="font-weight: 700; font-size: 0.9rem; color: var(--primary);">${m.title}</div>
                  <div style="font-size: 0.85rem; color: var(--text-main); margin-top: 0.2rem;">
                    <strong>Topics to Master:</strong> ${m.focus_topics}
                  </div>
                  <div class="project-tag">
                    💡 <strong>Suggested Project:</strong> ${m.suggested_project}
                  </div>
                </div>
              `).join("")}
            </div>
          ` : ''}

          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">
            Estimated effort: ~${r.estimated_effort_weeks} weeks of dedicated learning
          </div>
        </div>
      `).join("")}
    </div>

    <!-- Transparent Score Formula Breakdown -->
    <div class="card">
      <div class="card-header">
        <h3>📐 Mathematical Score Audit</h3>
      </div>
      <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem; text-align: left;">
        <thead>
          <tr style="border-bottom: 2px solid var(--border); color: var(--text-muted);">
            <th style="padding: 0.5rem;">Skill</th>
            <th style="padding: 0.5rem;">Student Level</th>
            <th style="padding: 0.5rem;">Required Level</th>
            <th style="padding: 0.5rem;">Calculation: min(S/R, 1.0)</th>
            <th style="padding: 0.5rem; text-align: right;">Contribution</th>
          </tr>
        </thead>
        <tbody>
          ${result.score_breakdown ? result.score_breakdown.map(b => `
            <tr style="border-bottom: 1px solid var(--border);">
              <td style="padding: 0.5rem; font-weight: 600;">${b.skill}</td>
              <td style="padding: 0.5rem;">${b.student_level}</td>
              <td style="padding: 0.5rem;">${b.required_level}</td>
              <td style="padding: 0.5rem; font-family: monospace;">min(${b.student_level}/${b.required_level}, 1.0) = ${b.ratio}</td>
              <td style="padding: 0.5rem; text-align: right; font-weight: 700;">${b.percentage_contribution}%</td>
            </tr>
          `).join("") : ""}
        </tbody>
      </table>
    </div>

    <!-- Mandatory Ethical Disclaimer -->
    <div class="disclaimer-box">
      ⚖️ <strong>Disclaimer:</strong> ${result.disclaimer}
    </div>
  `;
}

// Auto-initialize based on active page
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("assessment-form")) {
    initAssessmentPage();
  } else if (document.getElementById("skills-list")) {
    initDashboardPage();
  } else if (document.getElementById("results-content")) {
    initResultsPage();
  }
});
