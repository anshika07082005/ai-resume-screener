const API_BASE_URL = "https://ai-resume-screener-m7h7.onrender.com";
let chartInstance = null;


// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener(
  "DOMContentLoaded",
  async () => {

    const token = localStorage.getItem("token");


    if (!token || token === "ok") {

      localStorage.clear();

      window.location.href = "auth.html";

      return;
    }


    const authenticated =
      await verifyAuthentication();


    if (!authenticated) {

      localStorage.clear();

      window.location.href = "auth.html";

      return;
    }


    await loadHistory();

  }
);


// ============================================================
// AUTH CHECK
// ============================================================

async function verifyAuthentication() {

  const token =
    localStorage.getItem("token");


  try {

    const response = await fetch(
      `${API_BASE_URL}/me`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );


    return response.ok;


  } catch (error) {

    console.error(
      "Auth check failed:",
      error
    );

    return false;
  }
}


// ============================================================
// BUILD FORM DATA
// ============================================================

function buildFormData() {

  const resume =
    document
      .getElementById("resumeFile")
      .files[0];


  const jdFile =
    document
      .getElementById("jdFile")
      .files[0];


  const jdText =
    document
      .getElementById("jdText")
      .value
      .trim();


  const formData =
    new FormData();


  formData.append(
    "resume",
    resume
  );


  if (jdFile) {

    formData.append(
      "jd_file",
      jdFile
    );

    formData.append(
      "job_description",
      ""
    );

  } else {

    formData.append(
      "job_description",
      jdText
    );
  }


  return formData;
}


// ============================================================
// ANALYZE RESUME
// ============================================================

async function analyzeResume() {

  const resume =
    document
      .getElementById("resumeFile")
      .files[0];


  const jdFile =
    document
      .getElementById("jdFile")
      .files[0];


  const jdText =
    document
      .getElementById("jdText")
      .value
      .trim();


  const message =
    document.getElementById(
      "analysisMessage"
    );


  const button =
    document.getElementById(
      "analyzeBtn"
    );


  if (!resume) {

    alert(
      "Please upload a resume PDF."
    );

    return;
  }


  if (!jdFile && !jdText) {

    alert(
      "Please provide a job description."
    );

    return;
  }


  const token =
    localStorage.getItem("token");


  try {

    button.disabled = true;

    button.innerText =
      "Analyzing Resume...";


    message.innerText =
      "Running AI hiring intelligence analysis...";


    const response =
      await fetch(
        `${API_BASE_URL}/api/v2/screen`,
        {

          method: "POST",

          headers: {
            Authorization:
              `Bearer ${token}`
          },

          body: buildFormData()

        }
      );


    const data =
      await response.json();


    if (response.status === 401) {

      alert(
        "Session expired. Please log in again."
      );

      logout();

      return;
    }


    if (!response.ok) {

      message.innerText =
        data.detail ||
        "Resume analysis failed.";

      return;
    }


    renderResults(data);


    window.lastReportData =
      data;


    message.innerText =
      "Analysis completed successfully.";


    document
      .getElementById(
        "interviewSection"
      )
      .classList
      .add("hidden");


    await loadHistory();


  } catch (error) {

    console.error(
      "Screening error:",
      error
    );


    message.innerText =
      "Unable to connect to backend.";

  } finally {

    button.disabled = false;

    button.innerText =
      "🔍 Analyze Resume";
  }
}


// ============================================================
// RENDER SCREENING
// ============================================================

function renderResults(data) {

  document
    .getElementById("results")
    .classList
    .remove("hidden");


  document.getElementById(
    "candidateName"
  ).innerText =
    data.candidate_name || "N/A";


  document.getElementById(
    "jobTitle"
  ).innerText =
    data.job_title || "N/A";


  document.getElementById(
    "matchScore"
  ).innerText =
    formatScore(
      data.overall_score
    );


  const recommendation =
    document.getElementById(
      "recommendation"
    );


  recommendation.innerText =
    data.recommendation || "N/A";


  setRecommendationClass(
    recommendation,
    data.recommendation
  );


  renderSkillChips(
    "matchedSkills",
    data.matched_skills,
    "matched",
    "No required skills matched."
  );


  renderSkillChips(
    "missingSkills",
    data.missing_skills,
    "missing",
    "No missing required skills."
  );


  renderSkillChips(
    "preferredSkills",
    data.matched_preferred_skills,
    "preferred",
    "No preferred skills matched."
  );


  renderList(
    "strengthsList",
    data.strengths,
    "No strengths generated."
  );


  renderList(
    "weaknessesList",
    data.weaknesses,
    "No major weaknesses identified."
  );


  const breakdown =
    data.breakdown || {};


  setScore(
    "skillsScore",
    breakdown.skills
  );


  setScore(
    "preferredScore",
    breakdown.preferred_skills
  );


  setScore(
    "semanticScore",
    breakdown.semantic_similarity
  );


  setScore(
    "projectsScore",
    breakdown.projects
  );


  setScore(
    "experienceScore",
    breakdown.experience
  );


  setScore(
    "educationScore",
    breakdown.education
  );


  setScore(
    "certificationsScore",
    breakdown.certifications
  );


  drawChart(
    (data.matched_skills || []).length,
    (data.missing_skills || []).length
  );
}


// ============================================================
// INTERVIEW GENERATION
// ============================================================

async function generateInterview() {

  console.log(
    "Generate Interview clicked"
  );


  const resume =
    document
      .getElementById("resumeFile")
      .files[0];


  const jdFile =
    document
      .getElementById("jdFile")
      .files[0];


  const jdText =
    document
      .getElementById("jdText")
      .value
      .trim();


  const section =
    document.getElementById(
      "interviewSection"
    );


  const message =
    document.getElementById(
      "interviewMessage"
    );


  const button =
    document.getElementById(
      "interviewBtn"
    );


  if (!resume) {

    alert(
      "Please upload your resume first."
    );

    return;
  }


  if (!jdFile && !jdText) {

    alert(
      "Please provide a job description first."
    );

    return;
  }


  const token =
    localStorage.getItem("token");


  if (!token) {

    logout();

    return;
  }


  section.classList.remove(
    "hidden"
  );


  message.innerText =
    "Generating personalized interview questions...";


  try {

    button.disabled = true;

    button.innerText =
      "Generating Questions...";


    const response =
      await fetch(
        `${API_BASE_URL}/api/v2/interview/generate`,
        {

          method: "POST",

          headers: {

            Authorization:
              `Bearer ${token}`

          },

          body: buildFormData()

        }
      );


    console.log(
      "Interview status:",
      response.status
    );


    const data =
      await response.json();


    console.log(
      "Interview response:",
      data
    );


    if (response.status === 401) {

      message.innerText =
        "Authentication expired. Please log in again.";

      return;
    }


    if (!response.ok) {

      message.innerText =
        data.detail ||
        "Interview question generation failed.";

      return;
    }


    if (
      !data.questions
    ) {

      message.innerText =
        "The backend returned no interview questions.";

      return;
    }


    renderInterviewQuestions(
      data
    );


    message.innerText =
      "Interview questions generated successfully.";


    section.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });


  } catch (error) {

    console.error(
      "Interview frontend error:",
      error
    );


    message.innerText =
      "Unable to generate interview questions. Check browser console.";

  } finally {

    button.disabled = false;

    button.innerText =
      "🎯 Generate Interview Questions";
  }
}


// ============================================================
// RENDER INTERVIEW QUESTIONS
// ============================================================

function renderInterviewQuestions(
  data
) {

  console.log(
    "Rendering interview questions"
  );


  const questions =
    data.questions || {};


  document.getElementById(
    "interviewSubtitle"
  ).innerText =
    `${data.candidate_name || "Candidate"} • ${data.job_title || "Role"}`;


  renderQuestionList(
    "technicalQuestions",
    questions.technical_questions
  );


  renderQuestionList(
    "projectQuestions",
    questions.project_questions
  );


  renderQuestionList(
    "skillGapQuestions",
    questions.skill_gap_questions
  );


  renderQuestionList(
    "experienceQuestions",
    questions.experience_questions
  );


  renderQuestionList(
    "behavioralQuestions",
    questions.behavioral_questions
  );
}


// ============================================================
// QUESTION LIST
// ============================================================

function renderQuestionList(
  elementId,
  questions
) {

  const list =
    document.getElementById(
      elementId
    );


  if (!list) {

    console.error(
      `Missing HTML element: ${elementId}`
    );

    return;
  }


  list.innerHTML = "";


  if (
    !Array.isArray(questions) ||
    questions.length === 0
  ) {

    const item =
      document.createElement(
        "li"
      );


    item.innerText =
      "No questions generated for this category.";


    list.appendChild(item);

    return;
  }


  questions.forEach(
    question => {

      const item =
        document.createElement(
          "li"
        );


      item.innerText =
        question;


      list.appendChild(
        item
      );
    }
  );
}


// ============================================================
// SCORES
// ============================================================

function formatScore(value) {

  const number =
    Number(value);


  if (!Number.isFinite(number)) {
    return "0";
  }


  return number.toFixed(2);
}


function setScore(
  elementId,
  value
) {

  document.getElementById(
    elementId
  ).innerText =
    `${formatScore(value)}%`;
}


// ============================================================
// SKILL CHIPS
// ============================================================

function renderSkillChips(
  containerId,
  skills,
  className,
  emptyMessage
) {

  const container =
    document.getElementById(
      containerId
    );


  container.innerHTML = "";


  if (
    !Array.isArray(skills) ||
    skills.length === 0
  ) {

    const text =
      document.createElement(
        "p"
      );


    text.className =
      "empty-result";


    text.innerText =
      emptyMessage;


    container.appendChild(
      text
    );

    return;
  }


  skills.forEach(
    skill => {

      const span =
        document.createElement(
          "span"
        );


      span.className =
        `skill ${className}`;


      span.innerText =
        skill;


      container.appendChild(
        span
      );
    }
  );
}


// ============================================================
// LISTS
// ============================================================

function renderList(
  containerId,
  values,
  emptyMessage
) {

  const container =
    document.getElementById(
      containerId
    );


  container.innerHTML = "";


  if (
    !Array.isArray(values) ||
    values.length === 0
  ) {

    const li =
      document.createElement(
        "li"
      );


    li.innerText =
      emptyMessage;


    container.appendChild(
      li
    );

    return;
  }


  values.forEach(
    value => {

      const li =
        document.createElement(
          "li"
        );


      li.innerText =
        value;


      container.appendChild(
        li
      );
    }
  );
}


// ============================================================
// RECOMMENDATION
// ============================================================

function setRecommendationClass(
  element,
  recommendation
) {

  element.className =
    "recommendation-badge";


  const value =
    (
      recommendation || ""
    ).toLowerCase();


  if (
    value.includes("strong") ||
    value.includes("good")
  ) {

    element.classList.add(
      "recommendation-good"
    );

  } else if (
    value.includes("moderate")
  ) {

    element.classList.add(
      "recommendation-moderate"
    );

  } else {

    element.classList.add(
      "recommendation-low"
    );
  }
}


// ============================================================
// CHART
// ============================================================

function drawChart(
  matched,
  missing
) {

  const ctx =
    document.getElementById(
      "skillChart"
    );


  if (chartInstance) {
    chartInstance.destroy();
  }


  chartInstance =
    new Chart(
      ctx,
      {

        type: "pie",

        data: {

          labels: [
            "Matched",
            "Missing"
          ],

          datasets: [
            {

              data: [
                matched || 1,
                missing || 0
              ],

              backgroundColor: [
                "#10b981",
                "#ef4444"
              ],

              borderWidth: 0
            }
          ]
        },


        options: {

          responsive: true,

          plugins: {

            legend: {
              position: "bottom"
            }
          }
        }
      }
    );
}


// ============================================================
// HISTORY
// ============================================================

async function loadHistory() {

  const token =
    localStorage.getItem("token");


  const container =
    document.getElementById(
      "historyContent"
    );


  if (!token) {
    return;
  }


  try {

    const response =
      await fetch(
        `${API_BASE_URL}/api/v2/history`,
        {

          headers: {
            Authorization:
              `Bearer ${token}`
          }

        }
      );


    if (response.status === 401) {

      logout();

      return;
    }


    if (!response.ok) {

      container.innerHTML =
        `<p class="history-empty">Unable to load screening history.</p>`;

      return;
    }


    const history =
      await response.json();


    renderHistory(history);


  } catch (error) {

    console.error(
      "History error:",
      error
    );


    container.innerHTML =
      `<p class="history-empty">Unable to load screening history.</p>`;
  }
}


// ============================================================
// HISTORY TABLE
// ============================================================

function renderHistory(history) {

  const container =
    document.getElementById(
      "historyContent"
    );


  container.innerHTML = "";


  if (
    !Array.isArray(history) ||
    history.length === 0
  ) {

    container.innerHTML =
      `<p class="history-empty">No screening history yet.</p>`;

    return;
  }


  const wrapper =
    document.createElement(
      "div"
    );


  wrapper.className =
    "history-table-wrapper";


  const table =
    document.createElement(
      "table"
    );


  table.className =
    "history-table";


  table.innerHTML =
    `
      <thead>
        <tr>
          <th>Candidate</th>
          <th>Job Role</th>
          <th>Score</th>
          <th>Recommendation</th>
          <th>Date</th>
          <th>View</th>
        </tr>
      </thead>
      <tbody></tbody>
    `;


  const tbody =
    table.querySelector(
      "tbody"
    );


  history.forEach(
    record => {

      const row =
        document.createElement(
          "tr"
        );


      const date =
        record.created_at
          ? new Date(
              record.created_at
            ).toLocaleString()
          : "N/A";


      row.innerHTML =
        `
          <td>
            ${escapeHtml(
              record.candidate_name || "N/A"
            )}
          </td>

          <td>
            ${escapeHtml(
              record.job_title || "N/A"
            )}
          </td>

          <td>
            <strong>
              ${formatScore(
                record.overall_score
              )}%
            </strong>
          </td>

          <td>
            ${escapeHtml(
              record.recommendation || "N/A"
            )}
          </td>

          <td>
            ${escapeHtml(date)}
          </td>

          <td>

            <button
              class="view-result-btn"
              onclick="viewHistoryResult(${Number(record.id)})"
            >
              View
            </button>

          </td>
        `;


      tbody.appendChild(
        row
      );
    }
  );


  wrapper.appendChild(
    table
  );


  container.appendChild(
    wrapper
  );
}


// ============================================================
// VIEW HISTORY
// ============================================================

async function viewHistoryResult(
  screeningId
) {

  const token =
    localStorage.getItem("token");


  const response =
    await fetch(
      `${API_BASE_URL}/api/v2/history/${screeningId}`,
      {

        headers: {
          Authorization:
            `Bearer ${token}`
        }

      }
    );


  if (!response.ok) {

    alert(
      "Unable to load screening."
    );

    return;
  }


  const data =
    await response.json();


  renderResults(data);


  window.lastReportData =
    data;


  document
    .getElementById("results")
    .scrollIntoView({
      behavior: "smooth"
    });
}


// ============================================================
// REPORT
// ============================================================

function downloadReport() {

  const data =
    window.lastReportData;


  if (!data) {

    alert(
      "Please analyze a resume first."
    );

    return;
  }


  const normalizedScore =
    Number(
      data.overall_score || 0
    ) / 100;


  const matched =
    (
      data.matched_skills || []
    ).join(",");


  const missing =
    (
      data.missing_skills || []
    ).join(",");


  const url =
    `${API_BASE_URL}/download-report` +
    `?match_score=${encodeURIComponent(normalizedScore)}` +
    `&matched_skills=${encodeURIComponent(matched)}` +
    `&missing_skills=${encodeURIComponent(missing)}`;


  window.open(
    url,
    "_blank"
  );
}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(value) {

  const div =
    document.createElement(
      "div"
    );


  div.textContent =
    String(value);


  return div.innerHTML;
}


// ============================================================
// LOGOUT
// ============================================================

function logout() {

  localStorage.clear();

  window.location.href =
    "auth.html";
}