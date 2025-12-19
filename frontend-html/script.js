let chartInstance = null;

async function analyzeResume() {
  const resume = document.getElementById("resumeFile").files[0];
  const jdFile = document.getElementById("jdFile").files[0];
  const jdText = document.getElementById("jdText").value;

  if (!resume) {
    alert("Please upload a resume PDF");
    return;
  }

  const formData = new FormData();
  formData.append("resume", resume);

  if (jdFile) {
    formData.append("jd_file", jdFile);
  } else {
    formData.append("job_description", jdText);
  }

  const response = await fetch("http://127.0.0.1:8000/screen-pdf", {
    method: "POST",
    body: formData
  });

  const data = await response.json();
  renderResults(data);
}

function renderResults(data) {
  document.getElementById("results").classList.remove("hidden");

  // Match score
  document.getElementById("matchScore").innerText =
    Math.round(data.match_score * 100);

  // Predicted role
  document.getElementById("predictedRole").innerHTML =
    `<strong>Predicted Role:</strong> ${data.predicted_role || "N/A"}`;

  // ATS score
  document.getElementById("atsScore").innerHTML =
    `<strong>ATS Compatibility:</strong> ${Math.round((data.ats_score || 0) * 100)}%`;

  // Skills
  renderSkillChips("matchedSkills", data.matched_skills, "matched");
  renderSkillChips("missingSkills", data.missing_skills, "missing");

  // Suggestions
  const suggestionList = document.getElementById("resumeSuggestions");
  suggestionList.innerHTML = "";
  (data.resume_suggestions || []).forEach(s => {
    const li = document.createElement("li");
    li.textContent = s;
    suggestionList.appendChild(li);
  });

  // Learning roadmap
  const roadmapDiv = document.getElementById("learningRoadmap");
  roadmapDiv.innerHTML = "";
  if (data.learning_roadmap) {
    for (const skill in data.learning_roadmap) {
      const p = document.createElement("p");
      p.innerHTML = `<strong>${skill}:</strong> ${data.learning_roadmap[skill].join(" → ")}`;
      roadmapDiv.appendChild(p);
    }
  }

  // Chart
  drawChart(data.matched_skills.length, data.missing_skills.length);

  // Save data for report
  window.lastReportData = data;
}

function renderSkillChips(containerId, skills, className) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  (skills || []).forEach(skill => {
    const span = document.createElement("span");
    span.className = `skill ${className}`;
    span.innerText = skill;
    container.appendChild(span);
  });
}

function drawChart(matched, missing) {
  const ctx = document.getElementById("skillChart");

  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(ctx, {
    type: "pie",
    data: {
      labels: ["Matched", "Missing"],
      datasets: [{
        data: [matched, missing]
      }]
    }
  });
}

function downloadReport() {
  const d = window.lastReportData;
  if (!d) return;

  const url = `http://127.0.0.1:8000/download-report?match_score=${d.match_score}&matched_skills=${d.matched_skills.join(",")}&missing_skills=${d.missing_skills.join(",")}`;
  window.open(url, "_blank");
}

function logout() {
  localStorage.clear();
  window.location.href = "auth.html";
}
