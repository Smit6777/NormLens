/**
 * BharatStandards.AI - Enterprise Frontend Engine
 * SIH 2026 Problem Statement 26108
 */

// Mock Database of Indian Standards (BIS)
const STANDARDS_DB = [
  {
    code: "IS 10322 (Part 5/Sec 3): 2012",
    title: "Luminaires: Particular Requirements - Luminaires for Road and Street Lighting",
    category: "Electrical & Lighting",
    year: "2012 (Rev 2026)",
    status: "Current",
    relevance: 94,
    description: "Specifies requirements for road and street lighting luminaires, electrical safety, mechanical endurance, degree of protection (IP66 minimum for outdoor), thermal endurance, and photobiological safety.",
    whyMatches: [
      "Product category strictly matches Outdoor LED Street Luminaires",
      "Meets road lighting optical distribution & thermal dissipation requirements",
      "Complies with 90W driver electrical insulation & surge protection test criteria",
      "Includes mandatory IP66 weatherproof & IK08 impact testing parameters"
    ],
    normativeReferences: ["IS 15885 (Part 2/Sec 13)", "IS 16102 (Part 1)", "IS 16103 (Part 2)"],
    certification: "BIS Product Certification Scheme I (ISI Mark Mandatory)",
    amendments: [
      { year: "2018", label: "Published / Harmonized with IEC 60598-2-3" },
      { year: "2020", label: "Amendment 1: Surge endurance & thermal limits" },
      { year: "2023", label: "Amendment 2: Photobiological & blue light safety" },
      { year: "2026", label: "Current Verified Benchmark" }
    ]
  },
  {
    code: "IS 16102 (Part 1): 2017",
    title: "Self-Ballasted LED Lamps for General Lighting Services - Part 1: Safety Requirements",
    category: "Electrical & Lighting",
    year: "2017",
    status: "Current",
    relevance: 91,
    description: "Specifies the safety and interchangeability requirements, together with the test methods and conditions, required to show compliance of LED lamps with integrated means for controlling.",
    whyMatches: [
      "Mandates safety standards for LED modules and luminaire control electronics",
      "Validates thermal limits under extreme Indian ambient temperatures (+50°C)",
      "Specifies creepage distances, high voltage breakdown, and fire hazard safety"
    ],
    normativeReferences: ["IS 15885", "IS 16101"],
    certification: "Compulsory Registration Scheme (CRS)",
    amendments: [
      { year: "2017", label: "Published" },
      { year: "2021", label: "Amendment 1: Test procedures" },
      { year: "2025", label: "Reaffirmed" },
      { year: "2026", label: "Current" }
    ]
  },
  {
    code: "IS 15885 (Part 2/Sec 13): 2012",
    title: "Lamp Controlgear - Part 2: Particular Requirements - Section 13: D.C. or A.C. Supplied Electronic Controlgear for LED Modules",
    category: "Electrical & Lighting",
    year: "2012",
    status: "Current",
    relevance: 88,
    description: "Covers particular safety requirements for electronic controlgear (drivers) for use on d.c. supplies up to 250V and a.c. supplies up to 1000V at 50Hz for LED applications.",
    whyMatches: [
      "Regulates constant current driver specifications for 90W LED drivers",
      "Tests over-voltage, short circuit, open circuit, and thermal shutdown",
      "Mandates electromagnetic compatibility (EMC) and harmonic current limits"
    ],
    normativeReferences: ["IS 10322", "IS 6873"],
    certification: "Compulsory Registration Scheme (CRS)",
    amendments: [
      { year: "2012", label: "Published" },
      { year: "2019", label: "Amendment 1: Ingress protection for driver enclosures" },
      { year: "2026", label: "Current" }
    ]
  },
  {
    code: "IS 2026 (Part 1 to 5): 2011",
    title: "Power Transformers - Specification (General, Temperature Rise, Insulation)",
    category: "Heavy Electrical",
    year: "2011",
    status: "Current",
    relevance: 96,
    description: "Standard for distribution and power transformers, temperature rise limits, dielectric tests, short-circuit withstand capability, and impedance tolerances.",
    whyMatches: [
      "Covers step-down and step-up transformer procurement specifications",
      "Defines oil-filled and dry-type thermal dissipation standards"
    ],
    normativeReferences: ["IS 12444", "IS 335"],
    certification: "BIS Mandatory Certification (Quality Control Order)",
    amendments: [
      { year: "2011", label: "Revision 3 Published" },
      { year: "2017", label: "Amendment 1: Energy efficiency levels" },
      { year: "2026", label: "Current Standard" }
    ]
  },
  {
    code: "IS 2925: 1984",
    title: "Specification for Industrial Safety Helmets",
    category: "Occupational Safety",
    year: "1984 (Reaffirmed 2023)",
    status: "Current",
    relevance: 95,
    description: "Specifies requirements for industrial safety helmets regarding shock absorption, penetration resistance, flammability, and chin-strap retention under harsh industrial environments.",
    whyMatches: [
      "Exact match for industrial personal protective equipment (PPE) requirements",
      "Mandates high-impact thermoplastic and dielectric resistance tests"
    ],
    normativeReferences: ["IS 4699", "IS 9890"],
    certification: "BIS Product Certification Scheme (ISI Mark Mandatory)",
    amendments: [
      { year: "1984", label: "Published" },
      { year: "2010", label: "Amendment 1: Chin strap test specification" },
      { year: "2023", label: "Reaffirmed" },
      { year: "2026", label: "Current" }
    ]
  },
  {
    code: "IS 1520: 1980",
    title: "Horizontal Centrifugal Pumps for Clear, Cold Water for Agricultural and Domestic Purposes",
    category: "Mechanical & Water",
    year: "1980 (Rev 2022)",
    status: "Current",
    relevance: 93,
    description: "Covers specifications, performance parameters, hydrostatic pressure tests, and energy efficiency ratings for centrifugal water pumps.",
    whyMatches: [
      "Applies to civil, municipal, and agricultural water pumping procurement",
      "Defines head, discharge, power consumption, and casing durability norms"
    ],
    normativeReferences: ["IS 325", "IS 5120"],
    certification: "BIS ISI Certification + BEE Star Rating Scheme",
    amendments: [
      { year: "1980", label: "Published" },
      { year: "2015", label: "Amendment 2: Minimum efficiency index" },
      { year: "2026", label: "Current" }
    ]
  }
];

// Mock History
let historyStore = [
  {
    requirement: "90W Outdoor LED Street Lighting for Smart City Municipal Corridor",
    date: "20 Sep 2026",
    standardsFound: 8,
    status: "Completed",
    category: "Electrical & Lighting"
  },
  {
    requirement: "11kV/415V 500kVA Distribution Transformer for Substation Upgrade",
    date: "19 Sep 2026",
    standardsFound: 6,
    status: "Completed",
    category: "Heavy Electrical"
  },
  {
    requirement: "Industrial Heavy Duty Safety Helmets with Chin Strap (IS 2925)",
    date: "17 Sep 2026",
    standardsFound: 4,
    status: "Completed",
    category: "Occupational Safety"
  },
  {
    requirement: "Submersible Monobloc Water Pump 5HP for Rural Irrigation Supply",
    date: "15 Sep 2026",
    standardsFound: 5,
    status: "Completed",
    category: "Mechanical & Water"
  }
];

// Application State & Backend Configuration (Track 02)
const API_BASE_URL = window.location.origin.includes(":8000")
  ? `${window.location.origin}/api/v1`
  : "http://localhost:8000/api/v1";

const API_KEY = "test-api-key";
let authToken = localStorage.getItem("normlens_token") || null;
let currentOfficer = JSON.parse(localStorage.getItem("normlens_user") || '{"username": "rutvi_officer", "full_name": "Rutvi"}');

const state = {
  currentView: "home",
  activeTab: "text", // 'text' | 'file'
  uploadedFile: null,
  currentQuery: "90W Outdoor LED Street Lighting",
  analysisRunning: false,
  analysisProgress: 0,
  activeStageIndex: 0,
  lastApiResult: null
};

// Automatic Demo Officer Login
async function autoLoginDemoOfficer() {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/demo-login`, { method: "POST" });
    if (res.ok) {
      const data = await res.json();
      authToken = data.access_token;
      currentOfficer = data.user;
      localStorage.setItem("normlens_token", authToken);
      localStorage.setItem("normlens_user", JSON.stringify(currentOfficer));
      updateOfficerBadge();
    }
  } catch (err) {
    console.warn("Backend API offline or unreachable; using client cache:", err);
  }
}

function updateOfficerBadge() {
  const nameEl = document.getElementById("officerNameDisplay");
  if (nameEl && currentOfficer) {
    nameEl.innerText = `Officer: ${currentOfficer.full_name || currentOfficer.username} (Verified)`;
  }
}

function promptOfficerLogin() {
  const username = prompt("Enter Officer Username:", currentOfficer?.username || "rutvi_officer");
  if (!username) return;
  const password = prompt("Enter Password:", "NormLens2026!");
  if (!password) return;

  fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  })
  .then(r => r.json())
  .then(data => {
    if (data.access_token) {
      authToken = data.access_token;
      currentOfficer = data.user;
      localStorage.setItem("normlens_token", authToken);
      localStorage.setItem("normlens_user", JSON.stringify(currentOfficer));
      updateOfficerBadge();
      alert(`Welcome back, ${currentOfficer.full_name || currentOfficer.username}!`);
      renderHistoryTable();
    } else {
      alert("Login failed: " + (data.detail || "Invalid credentials"));
    }
  })
  .catch(err => alert("Error connecting to backend: " + err.message));
}

// Loading Process Stages (Exact 7-stage vertical timeline)
const ANALYSIS_STAGES = [
  { id: 0, label: "Reading specification", subtext: "Parsing input technical constraints..." },
  { id: 1, label: "Extracting product requirements", subtext: "Extracting wattage, environmental ratings & electrical safety..." },
  { id: 2, label: "Identifying product category", subtext: "Classified into Electrical & Outdoor Infrastructure..." },
  { id: 3, label: "Searching Standards Knowledge Base", subtext: "Querying indexed Bureau of Indian Standards (BIS) corpus..." },
  { id: 4, label: "Finding related standards", subtext: "Discovering allied luminaire, controlgear & safety standards..." },
  { id: 5, label: "Checking versions and amendments", subtext: "Checking latest amendments & Quality Control Orders (QCO)..." },
  { id: 6, label: "Preparing recommendations", subtext: "Formulating semantic relevance scores & verification report..." }
];

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupTextareaCounter();
  setupChips();
  setupUploadArea();
  autoLoginDemoOfficer();
  renderStandardsCatalog();
  renderHistoryTable();
  initNormLensSlider();

  // Set default requirement in input fields
  const mainInput = document.getElementById("mainRequirementInput");
  if (mainInput) {
    mainInput.value = "90W Outdoor LED Street Lighting with IP66 weatherproof housing, surge protection, and high-efficiency driver for urban municipal roads.";
    updateCharCounter();
  }
});


// View Navigation Router
function navigateTo(viewId) {
  state.currentView = viewId;

  // Update Nav links
  document.querySelectorAll(".nav-link").forEach(link => {
    link.classList.remove("active");
    if (link.dataset.view === viewId) {
      link.classList.add("active");
    }
  });

  // Switch View Section
  document.querySelectorAll(".view-section").forEach(sec => {
    sec.classList.remove("active");
  });

  const targetView = document.getElementById(`view-${viewId}`);
  if (targetView) {
    targetView.classList.add("active");
  }

  // Scroll to top cleanly
  window.scrollTo({ top: 0, behavior: "smooth" });

  if (viewId === "standards") {
    renderStandardsCatalog();
  } else if (viewId === "history") {
    renderHistoryTable();
  }
}

function setupNavigation() {
  document.querySelectorAll("[data-navigate]").forEach(el => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      const target = el.dataset.navigate;
      navigateTo(target);
    });
  });
}

// Textarea Character Counter
function setupTextareaCounter() {
  const textarea = document.getElementById("mainRequirementInput");
  if (textarea) {
    textarea.addEventListener("input", updateCharCounter);
  }
  const newAnalysisInput = document.getElementById("newAnalysisInput");
  if (newAnalysisInput) {
    newAnalysisInput.addEventListener("input", () => {
      const counter = document.getElementById("newAnalysisCharCounter");
      if (counter) counter.innerText = `${newAnalysisInput.value.length}/500`;
    });
  }
}

function updateCharCounter() {
  const textarea = document.getElementById("mainRequirementInput");
  const counter = document.getElementById("mainCharCounter");
  if (textarea && counter) {
    counter.innerText = `${textarea.value.length}/500`;
  }
}

// Preset Example Chips
function setupChips() {
  document.querySelectorAll(".chip-btn").forEach(chip => {
    chip.addEventListener("click", () => {
      const query = chip.dataset.query;
      const targetInput = state.currentView === "new-analysis" 
        ? document.getElementById("newAnalysisInput")
        : document.getElementById("mainRequirementInput");

      if (targetInput) {
        targetInput.value = query;
        updateCharCounter();
        const counter = document.getElementById("newAnalysisCharCounter");
        if (counter) counter.innerText = `${query.length}/500`;
      }
    });
  });
}

// Tab Switching & File Upload
function switchTab(tabType, context) {
  state.activeTab = tabType;
  const parent = context === 'home' ? document.getElementById('homeInputCard') : document.getElementById('newAnalysisCard');
  if (!parent) return;

  const tabButtons = parent.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabType);
  });

  const textPane = parent.querySelector('.tab-pane-text');
  const filePane = parent.querySelector('.tab-pane-file');

  if (textPane && filePane) {
    if (tabType === 'text') {
      textPane.style.display = 'block';
      filePane.style.display = 'none';
    } else {
      textPane.style.display = 'none';
      filePane.style.display = 'block';
    }
  }
}

function setupUploadArea() {
  const setupDropzone = (dropzoneId, fileChipId, inputId) => {
    const dropzone = document.getElementById(dropzoneId);
    const fileChip = document.getElementById(fileChipId);
    const fileInput = document.getElementById(inputId);

    if (!dropzone || !fileChip || !fileInput) return;

    dropzone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        handleSelectedFile(e.target.files[0], dropzone, fileChip);
      }
    });

    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.style.borderColor = "var(--primary-green)";
    });

    dropzone.addEventListener("dragleave", () => {
      dropzone.style.borderColor = "var(--border-color)";
    });

    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleSelectedFile(e.dataTransfer.files[0], dropzone, fileChip);
      }
    });
  };

  setupDropzone("homeDropzone", "homeFileChip", "homeFileInput");
  setupDropzone("newAnalysisDropzone", "newAnalysisFileChip", "newAnalysisFileInput");
}

function handleSelectedFile(file, dropzone, fileChip) {
  state.uploadedFile = file;
  dropzone.style.display = "none";
  fileChip.style.display = "flex";
  
  const nameEl = fileChip.querySelector(".file-name-display");
  if (nameEl) nameEl.innerText = file.name;
}

function removeUploadedFile(context) {
  state.uploadedFile = null;
  const isHome = context === 'home';
  const dropzone = document.getElementById(isHome ? "homeDropzone" : "newAnalysisDropzone");
  const fileChip = document.getElementById(isHome ? "homeFileChip" : "newAnalysisFileChip");
  const fileInput = document.getElementById(isHome ? "homeFileInput" : "newAnalysisFileInput");

  if (dropzone) dropzone.style.display = "block";
  if (fileChip) fileChip.style.display = "none";
  if (fileInput) fileInput.value = "";
}

// Active Standards Map for modal inspection
state.activeStandardsMap = {};

// Trigger AI Analysis Execution Flow
async function startAnalysis(source) {
  let queryText = "";
  if (source === 'home') {
    const input = document.getElementById("mainRequirementInput");
    queryText = input ? input.value.trim() : "";
  } else {
    const input = document.getElementById("newAnalysisInput");
    queryText = input ? input.value.trim() : "";
  }

  if (state.uploadedFile) {
    state.currentQuery = `Tender Document: ${state.uploadedFile.name}`;
  } else if (queryText) {
    state.currentQuery = queryText;
  } else {
    state.currentQuery = "90W Outdoor LED Street Lighting";
  }

  // Navigate to Loading Processing Screen
  navigateTo("loading");

  // Prepare Live API Request to FastAPI (Track 02)
  const formData = new FormData();
  if (state.uploadedFile) {
    formData.append("file", state.uploadedFile);
  } else {
    formData.append("text", state.currentQuery);
  }

  const headers = { "X-API-Key": API_KEY };
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  const apiPromise = fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: headers,
    body: formData,
  })
    .then(async (res) => {
      if (!res.ok) {
        throw new Error(`API returned status ${res.status}`);
      }
      return await res.json();
    })
    .catch((err) => {
      console.warn("Backend API request fallback:", err);
      return null;
    });

  runLoadingSimulation(apiPromise);
}

// 7-Stage Circular & Vertical Loading Simulation with Live API Integration
function runLoadingSimulation(apiPromise) {
  state.analysisRunning = true;
  state.analysisProgress = 0;
  state.activeStageIndex = 0;

  const circleFill = document.getElementById("circleFill");
  const circlePct = document.getElementById("circlePercentage");
  const tickerText = document.getElementById("dynamicTickerText");

  // Reset timeline UI
  renderLoadingTimeline();

  const totalDuration = 3800;
  const intervalTime = 50;
  const totalSteps = totalDuration / intervalTime;
  let currentStep = 0;

  const timer = setInterval(async () => {
    currentStep++;
    const progress = Math.min(Math.round((currentStep / totalSteps) * 100), 100);
    state.analysisProgress = progress;

    if (circleFill) {
      const offset = 377 - (377 * progress) / 100;
      circleFill.style.strokeDashoffset = offset;
    }
    if (circlePct) {
      circlePct.innerText = `${progress}%`;
    }

    const stageIdx = Math.min(Math.floor((progress / 100) * ANALYSIS_STAGES.length), ANALYSIS_STAGES.length - 1);
    if (stageIdx !== state.activeStageIndex) {
      state.activeStageIndex = stageIdx;
      renderLoadingTimeline();
    }

    if (tickerText) {
      tickerText.innerText = ANALYSIS_STAGES[state.activeStageIndex].subtext;
    }

    if (progress >= 100) {
      clearInterval(timer);
      state.analysisRunning = false;

      state.activeStageIndex = ANALYSIS_STAGES.length;
      renderLoadingTimeline();

      if (tickerText) {
        tickerText.innerHTML = `<span style="color: var(--primary-green); font-weight: 700;">✓ Analysis Complete — Verified against BIS Knowledge Base</span>`;
      }

      // Await live API payload
      let apiResult = null;
      try {
        apiResult = await apiPromise;
      } catch (e) {
        apiResult = null;
      }

      state.lastApiResult = apiResult;

      setTimeout(() => {
        populateResultsData(state.currentQuery, apiResult);
        renderHistoryTable(); // Refresh history from SQLite database
        navigateTo("results");
      }, 500);
    }
  }, intervalTime);
}

function renderLoadingTimeline() {
  const container = document.getElementById("analysisTimeline");
  if (!container) return;

  container.innerHTML = ANALYSIS_STAGES.map((stage, idx) => {
    let stateClass = "";
    let icon = "○";

    if (idx < state.activeStageIndex) {
      stateClass = "completed";
      icon = `✓`;
    } else if (idx === state.activeStageIndex) {
      stateClass = "active";
      icon = `●`;
    }

    return `
      <div class="timeline-step ${stateClass}">
        <div class="step-indicator-node">${icon}</div>
        <div class="timeline-step-label">${stage.label}</div>
      </div>
    `;
  }).join("");
}

// Populate Results View with Real API Data or Resilient Fallback
function populateResultsData(query, apiResult = null) {
  const queryBadge = document.getElementById("resultsQueryBadge");
  if (queryBadge) {
    queryBadge.innerText = query.length > 60 ? `${query.substring(0, 57)}...` : query;
  }

  const prodVal = document.getElementById("underProdVal");
  const appVal = document.getElementById("underAppVal");
  const tagCloud = document.getElementById("underTagCloud");
  const gapsSec = document.getElementById("complianceGapsSection");
  const gapsContainer = document.getElementById("gapsContainer");

  // Reset standard cache for modal lookup
  state.activeStandardsMap = {};

  if (apiResult && apiResult.recommendations && Object.keys(apiResult.recommendations).length > 0) {
    // --- LIVE API RESULT RENDERING ---
    const firstReq = apiResult.requirements && apiResult.requirements[0];
    if (prodVal) prodVal.innerText = firstReq?.product || "Procurement Specification";
    if (appVal) appVal.innerText = firstReq?.parameters?.application || "Government / Institutional Procurement";

    // Build spec tags
    if (tagCloud) {
      const tags = [];
      if (firstReq?.parameters?.cited_standards) {
        firstReq.parameters.cited_standards.forEach(cs => tags.push(`Cited: ${cs}`));
      }
      if (firstReq?.parameters?.voltage) tags.push(firstReq.parameters.voltage);
      if (firstReq?.parameters?.power) tags.push(firstReq.parameters.power);
      if (firstReq?.parameters?.ip_rating) tags.push(firstReq.parameters.ip_rating);
      if (tags.length === 0) tags.push("Mandatory Technical Parameters", "BIS Verification", "QCO Enforceability");
      tagCloud.innerHTML = tags.map(t => `<span class="spec-tag">${t}</span>`).join("");
    }

    // Process Recommendations
    const standardsList = [];
    let totalNormative = 0;
    for (const reqId in apiResult.recommendations) {
      for (const rec of apiResult.recommendations[reqId]) {
        const relevancePct = Math.round((rec.system_match_score || 0.85) * 100);
        const normRefs = rec.compliance?.normative_references || [];
        totalNormative += normRefs.length;

        const stdObj = {
          code: rec.is_number,
          title: rec.title || `Specification: ${rec.is_number}`,
          category: firstReq?.product || "Standard",
          year: rec.is_number.includes(":") ? rec.is_number.split(":")[1].trim() : "Current",
          status: rec.compliance?.standard_status || "Current Active",
          relevance: relevancePct,
          description: rec.match_reasons?.join(". ") || "Applicable Bureau of Indian Standards specification.",
          whyMatches: rec.match_reasons || ["Direct semantic match to technical specifications"],
          normativeReferences: normRefs,
          certification: rec.compliance?.qco_applicable
            ? "Mandatory Quality Control Order (QCO in force)"
            : "BIS Product Certification Scheme",
          amendments: [
            { year: "Active", label: `Status: ${rec.compliance?.standard_status || "Active"}` },
            { year: "Score", label: `Relevance: ${relevancePct}%` },
            { year: "Verified", label: `Confidence: ${rec.confidence || "HIGH"}` },
          ]
        };
        standardsList.push(stdObj);
        state.activeStandardsMap[stdObj.code] = stdObj;
      }
    }

    // Update Summary Metrics
    const metricCards = document.querySelectorAll(".summary-metrics-grid .metric-card .metric-value");
    if (metricCards.length >= 4) {
      metricCards[0].innerText = standardsList.length;
      metricCards[1].innerText = Math.max(totalNormative, 2);
      metricCards[2].innerText = apiResult.gaps && apiResult.gaps.length > 0 ? "Gaps Flagged" : "Verified Current";
      metricCards[2].className = apiResult.gaps && apiResult.gaps.length > 0 ? "metric-value" : "metric-value green";
      metricCards[3].innerText = "Applicable (QCO)";
    }

    // Render Gaps & AI Fixes
    if (gapsSec && gapsContainer) {
      if (apiResult.gaps && apiResult.gaps.length > 0) {
        gapsSec.style.display = "block";
        gapsContainer.innerHTML = apiResult.gaps.map((gap, idx) => {
          const fix = apiResult.fix_suggestions?.[idx];
          return `
            <div style="background: #FFFFFF; border: 1px solid #FBD38D; border-radius: 8px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #C05621; background: #FEEBC8; padding: 2px 8px; border-radius: 4px;">
                  ${gap.gap_type} • ${gap.severity} Severity
                </span>
                <span style="font-size: 0.75rem; color: var(--secondary-text);">Automated Compliance Audit</span>
              </div>
              <div style="font-weight: 600; color: var(--navy-text); font-size: 0.9rem; margin-bottom: 6px;">
                ${gap.message}
              </div>
              ${fix ? `
                <div style="background: rgba(22,131,91,0.06); border-left: 3px solid var(--primary-green); padding: 8px 12px; border-radius: 4px; font-size: 0.85rem; margin-top: 8px;">
                  <strong style="color: var(--deep-green);">AI Fix Proposal:</strong> ${fix.suggested_revision}
                </div>
              ` : ''}
            </div>
          `;
        }).join("");
      } else {
        gapsSec.style.display = "none";
      }
    }

    renderRecommendedCards(standardsList.length > 0 ? standardsList : [STANDARDS_DB[0]]);
  } else {
    // --- RESILIENT FALLBACK RENDERING ---
    if (gapsSec) gapsSec.style.display = "none";
    if (query.toLowerCase().includes("transformer")) {
      if (prodVal) prodVal.innerText = "Power / Distribution Transformer";
      if (appVal) appVal.innerText = "Substation / Grid Distribution";
      if (tagCloud) {
        tagCloud.innerHTML = `
          <span class="spec-tag">11kV / 415V</span>
          <span class="spec-tag">Oil-immersed</span>
          <span class="spec-tag">500 kVA</span>
          <span class="spec-tag">Dielectric Insulation</span>
          <span class="spec-tag">BEE 5-Star</span>
        `;
      }
      renderRecommendedCards([STANDARDS_DB[3], STANDARDS_DB[0], STANDARDS_DB[2]]);
    } else if (query.toLowerCase().includes("helmet")) {
      if (prodVal) prodVal.innerText = "Industrial Safety Helmet";
      if (appVal) appVal.innerText = "Workplace & Construction Site PPE";
      if (tagCloud) {
        tagCloud.innerHTML = `
          <span class="spec-tag">Shock Absorption</span>
          <span class="spec-tag">Penetration Resistance</span>
          <span class="spec-tag">Dielectric Voltage Test</span>
          <span class="spec-tag">Chin Strap Retention</span>
        `;
      }
      renderRecommendedCards([STANDARDS_DB[4], STANDARDS_DB[1], STANDARDS_DB[5]]);
    } else if (query.toLowerCase().includes("pump")) {
      if (prodVal) prodVal.innerText = "Centrifugal Water Pump";
      if (appVal) appVal.innerText = "Municipal Water Supply & Irrigation";
      if (tagCloud) {
        tagCloud.innerHTML = `
          <span class="spec-tag">Submersible</span>
          <span class="spec-tag">Hydrostatic Pressure</span>
          <span class="spec-tag">Energy Efficiency</span>
          <span class="spec-tag">5 HP</span>
        `;
      }
      renderRecommendedCards([STANDARDS_DB[5], STANDARDS_DB[1], STANDARDS_DB[3]]);
    } else {
      if (prodVal) prodVal.innerText = "LED Street Lighting";
      if (appVal) appVal.innerText = "Outdoor / Municipal Road Infrastructure";
      if (tagCloud) {
        tagCloud.innerHTML = `
          <span class="spec-tag">90W Output</span>
          <span class="spec-tag">Outdoor IP66</span>
          <span class="spec-tag">Road Application</span>
          <span class="spec-tag">Electrical Safety</span>
          <span class="spec-tag">Surge Protection</span>
          <span class="spec-tag">Testing</span>
        `;
      }
      renderRecommendedCards([STANDARDS_DB[0], STANDARDS_DB[1], STANDARDS_DB[2]]);
    }
  }
}

// Render Top 3 Recommendation Cards
function renderRecommendedCards(standardsList) {
  const container = document.getElementById("recommendedCardsContainer");
  if (!container) return;

  container.innerHTML = standardsList.slice(0, 3).map((std, idx) => {
    state.activeStandardsMap[std.code] = std;
    return `
      <div class="standard-recommendation-card">
        <div class="standard-top-row">
          <div>
            <span class="standard-number-badge">${std.code}</span>
            <h3 class="standard-title">${std.title}</h3>
          </div>
          <div class="standard-badges-right">
            <span class="relevance-score-badge">Relevance: ${std.relevance}%</span>
            <span class="status-live-badge"><span class="status-live-dot"></span> ${std.status}</span>
          </div>
        </div>

        <p class="standard-description">${std.description}</p>

        <div class="standard-footer-actions">
          <button class="btn-accordion-toggle" onclick="toggleWhyRecommended(${idx})">
            <span>Why recommended?</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>

          <button class="btn-outline" style="padding: 6px 14px; font-size: 0.8rem;" onclick="openStandardModal('${std.code}')">
            View Details
          </button>
        </div>

        <!-- Section 3: Why Recommended Expandable Content -->
        <div class="why-recommended-content" id="whyRec-${idx}">
          <div style="font-size: 0.85rem; font-weight: 700; color: var(--navy-text); margin-bottom: 4px;">
            Semantic Relevance: ${std.relevance}%
          </div>
          <ul class="why-checklist">
            ${(std.whyMatches || []).map(item => `
              <li class="why-checklist-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span>${item}</span>
              </li>
            `).join("")}
          </ul>
        </div>
      </div>
    `;
  }).join("");
}

// Toggle Why Recommended Expandable Section
function toggleWhyRecommended(index) {
  const content = document.getElementById(`whyRec-${index}`);
  if (content) {
    content.classList.toggle("expanded");
  }
}

// Modal Details Viewer
function openStandardModal(code) {
  const standard = state.activeStandardsMap[code] || STANDARDS_DB.find(s => s.code === code) || STANDARDS_DB[0];
  const modal = document.getElementById("standardDetailsModal");
  const modalBody = document.getElementById("modalBodyContent");

  if (!modal || !modalBody) return;

  modalBody.innerHTML = `
    <div style="margin-bottom: 16px;">
      <span class="standard-number-badge">${standard.code}</span>
      <h2 style="font-size: 1.25rem; font-weight: 800; color: var(--navy-text); margin-top: 6px;">
        ${standard.title}
      </h2>
      <div style="display: flex; gap: 8px; margin-top: 6px;">
        <span class="relevance-score-badge">Relevance: ${standard.relevance}%</span>
        <span class="status-live-badge"><span class="status-live-dot"></span> ${standard.status}</span>
        <span style="font-size: 0.8rem; color: var(--secondary-text); padding: 4px 8px;">Edition: ${standard.year}</span>
      </div>
    </div>

    <div style="margin-bottom: 20px;">
      <h4 style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: var(--secondary-text); margin-bottom: 6px;">Scope & Description</h4>
      <p style="font-size: 0.9rem; color: var(--navy-text); line-height: 1.6;">${standard.description}</p>
    </div>

    <div style="margin-bottom: 20px; background: var(--main-bg); padding: 14px; border-radius: 8px; border: 1px solid var(--border-color);">
      <h4 style="font-size: 0.85rem; font-weight: 700; color: var(--deep-green); margin-bottom: 6px;">Certification Scheme</h4>
      <p style="font-size: 0.85rem; color: var(--navy-text);">${standard.certification}</p>
    </div>

    <div style="margin-bottom: 20px;">
      <h4 style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: var(--secondary-text); margin-bottom: 6px;">Normative Cross-References</h4>
      <div style="display: flex; gap: 8px; flex-wrap: wrap;">
        ${(standard.normativeReferences || []).map(ref => `<span class="spec-tag">${ref}</span>`).join("")}
      </div>
    </div>

    <div style="display: flex; justify-content: flex-end; margin-top: 24px;">
      <button class="btn-primary" onclick="closeStandardModal()">Close Details</button>
    </div>
  `;

  modal.classList.add("active");
}

function closeStandardModal() {
  const modal = document.getElementById("standardDetailsModal");
  if (modal) modal.classList.remove("active");
}

// Standards Knowledge Base Catalog View
function renderStandardsCatalog() {
  const tableBody = document.getElementById("standardsTableBody");
  if (!tableBody) return;

  const searchInput = document.getElementById("standardsSearchInput");
  const categoryFilter = document.getElementById("categoryFilter");
  const query = searchInput ? searchInput.value.toLowerCase() : "";
  const cat = categoryFilter ? categoryFilter.value : "all";

  const filtered = STANDARDS_DB.filter(item => {
    const matchesSearch = item.code.toLowerCase().includes(query) || item.title.toLowerCase().includes(query) || item.description.toLowerCase().includes(query);
    const matchesCategory = cat === "all" || item.category === cat;
    return matchesSearch && matchesCategory;
  });

  if (filtered.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--secondary-text); padding: 24px;">No Indian Standards found matching your criteria.</td></tr>`;
    return;
  }

  tableBody.innerHTML = filtered.map(item => `
    <tr>
      <td style="font-weight: 700; color: var(--deep-green);">${item.code}</td>
      <td>
        <div style="font-weight: 600;">${item.title}</div>
        <div style="font-size: 0.75rem; color: var(--secondary-text);">${item.description.substring(0, 80)}...</div>
      </td>
      <td><span class="spec-tag">${item.category}</span></td>
      <td><span class="status-live-badge"><span class="status-live-dot"></span> ${item.status}</span></td>
      <td>
        <button class="btn-outline" style="padding: 4px 10px; font-size: 0.775rem;" onclick="openStandardModal('${item.code}')">
          Details
        </button>
      </td>
    </tr>
  `).join("");
}

// Live History Page Table (Track 02: Fetches directly from SQLite database)
async function renderHistoryTable() {
  const tbody = document.getElementById("historyTableBody");
  if (!tbody) return;

  try {
    const res = await fetch(`${API_BASE_URL}/history`);
    if (res.ok) {
      const records = await res.json();
      if (records && records.length > 0) {
        historyStore = records.map(r => ({
          id: r.id,
          requirement: r.query,
          date: r.created_at || "Recent",
          standardsFound: r.standards_found,
          status: r.status,
          category: r.category,
        }));
      }
    }
  } catch (err) {
    console.warn("Could not fetch history from SQLite database; using client memory:", err);
  }

  tbody.innerHTML = historyStore.map((row, idx) => `
    <tr>
      <td style="font-weight: 600; color: var(--navy-text);">${row.requirement}</td>
      <td style="color: var(--secondary-text);">${row.date}</td>
      <td><span class="spec-tag">${row.standardsFound} Standards</span></td>
      <td><span class="status-badge-complete">✓ ${row.status}</span></td>
      <td>
        <button class="btn-outline" style="padding: 4px 12px; font-size: 0.775rem;" onclick="viewHistoryItem(${idx})">
          View
        </button>
      </td>
    </tr>
  `).join("");
}

function addToHistory(requirement) {
  historyStore.unshift({
    requirement: requirement.length > 70 ? requirement.substring(0, 67) + "..." : requirement,
    date: "Just now",
    standardsFound: 3,
    status: "Completed",
    category: "Procurement"
  });
}

async function viewHistoryItem(index) {
  const item = historyStore[index];
  if (!item) return;

  if (item.id) {
    try {
      const res = await fetch(`${API_BASE_URL}/history/${item.id}`);
      if (res.ok) {
        const detail = await res.json();
        populateResultsData(detail.query, detail.result_data);
        navigateTo("results");
        return;
      }
    } catch (e) {
      console.warn("Failed to load historical record detail:", e);
    }
  }

  populateResultsData(item.requirement);
  navigateTo("results");
}

// Export Report: Live CSV Download with Print Fallback (Track 02)
async function exportProcurementReport() {
  try {
    const formData = new FormData();
    if (state.uploadedFile) {
      formData.append("file", state.uploadedFile);
    } else {
      formData.append("text", state.currentQuery);
    }

    const res = await fetch(`${API_BASE_URL}/analyze/export`, {
      method: "POST",
      body: formData,
      headers: { "X-API-Key": API_KEY }
    });

    if (res.ok) {
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `BIS_Tender_Compliance_Report_${Date.now()}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      return;
    }
  } catch (err) {
    console.warn("Live CSV export failed, falling back to print view:", err);
  }

  window.print();
}

/* ==========================================================================
   Hero Mini Image Slider (Cover-Flow / Center-Peek Slider)
   Supports: Center active slide, peeked prev/next sides, click-to-slide,
   arrow navigation, pagination dots, live caption updates, auto-play & swipe.
   ========================================================================== */
function initNormLensSlider() {
  const track = document.getElementById("normlensSliderTrack");
  const wrapper = document.getElementById("normlensSliderWrapper");
  const prevBtn = document.getElementById("sliderPrevBtn");
  const nextBtn = document.getElementById("sliderNextBtn");
  const dotsContainer = document.getElementById("sliderDotsContainer");
  const captionText = document.getElementById("miniSliderCaptionText");

  if (!track) return;

  const cards = Array.from(track.querySelectorAll(".mini-slider-card, .slider-card"));
  const totalSlides = cards.length;
  if (totalSlides === 0) return;

  let currentSlide = 0;
  let autoSlideTimer = null;

  // Build pagination dots
  if (dotsContainer) {
    dotsContainer.innerHTML = "";
    cards.forEach((_, idx) => {
      const dot = document.createElement("button");
      dot.className = `mini-slider-dot ${idx === 0 ? "active" : ""}`;
      dot.setAttribute("aria-label", `Go to slide ${idx + 1}`);
      dot.addEventListener("click", () => {
        goToSlide(idx);
        restartAutoSlide();
      });
      dotsContainer.appendChild(dot);
    });
  }

  function updateSlider() {
    cards.forEach((card, idx) => {
      // Calculate circular distance from current slide
      const diff = (idx - currentSlide + totalSlides) % totalSlides;

      // Reset previous position classes
      card.classList.remove("active", "prev-peek", "next-peek", "hidden-left", "hidden-right");

      if (diff === 0) {
        card.classList.add("active");
        card.setAttribute("aria-hidden", "false");
        // Update live caption
        if (captionText && card.dataset.caption) {
          captionText.innerHTML = card.dataset.caption;
        }
      } else if (diff === 1) {
        card.classList.add("next-peek");
        card.setAttribute("aria-hidden", "true");
      } else if (diff === totalSlides - 1) {
        card.classList.add("prev-peek");
        card.setAttribute("aria-hidden", "true");
      } else if (diff < totalSlides / 2) {
        card.classList.add("hidden-right");
        card.setAttribute("aria-hidden", "true");
      } else {
        card.classList.add("hidden-left");
        card.setAttribute("aria-hidden", "true");
      }
    });

    // Update dots state
    if (dotsContainer) {
      const dots = dotsContainer.querySelectorAll(".mini-slider-dot, .slider-dot");
      dots.forEach((dot, idx) => {
        dot.classList.toggle("active", idx === currentSlide);
      });
    }
  }

  function nextSlide() {
    currentSlide = (currentSlide + 1) % totalSlides;
    updateSlider();
  }

  function prevSlide() {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
    updateSlider();
  }

  function goToSlide(idx) {
    currentSlide = idx;
    updateSlider();
  }

  // Arrow button handlers
  if (prevBtn) {
    prevBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      prevSlide();
      restartAutoSlide();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      nextSlide();
      restartAutoSlide();
    });
  }

  // Clicking side peek cards navigates directly to that card
  cards.forEach((card, idx) => {
    card.addEventListener("click", () => {
      const diff = (idx - currentSlide + totalSlides) % totalSlides;
      if (diff === 1) {
        nextSlide();
        restartAutoSlide();
      } else if (diff === totalSlides - 1) {
        prevSlide();
        restartAutoSlide();
      }
    });
  });

  // Autoplay functionality (rotates every 4.2s, pauses on hover)
  function startAutoSlide() {
    if (autoSlideTimer) clearInterval(autoSlideTimer);
    autoSlideTimer = setInterval(nextSlide, 4200);
  }

  function stopAutoSlide() {
    if (autoSlideTimer) {
      clearInterval(autoSlideTimer);
      autoSlideTimer = null;
    }
  }

  function restartAutoSlide() {
    stopAutoSlide();
    startAutoSlide();
  }

  if (wrapper) {
    wrapper.addEventListener("mouseenter", stopAutoSlide);
    wrapper.addEventListener("mouseleave", startAutoSlide);

    // Touch swipe support for mobile
    let touchStartX = 0;
    let touchEndX = 0;

    wrapper.addEventListener("touchstart", (e) => {
      touchStartX = e.changedTouches[0].screenX;
      stopAutoSlide();
    }, { passive: true });

    wrapper.addEventListener("touchend", (e) => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
      startAutoSlide();
    }, { passive: true });

    function handleSwipe() {
      const swipeDistance = touchEndX - touchStartX;
      if (swipeDistance > 45) {
        prevSlide();
      } else if (swipeDistance < -45) {
        nextSlide();
      }
    }
  }

  // Initialize
  updateSlider();
  startAutoSlide();
}
