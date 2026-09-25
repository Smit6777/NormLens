/**
 * BharatStandards.AI - Enterprise Frontend Engine
 * SIH 2026 Problem Statement 26108
 */


const API_BASE_URL = 'YOUR_LOCALTUNNEL_URL_HERE/api/v1';

// Removed - using live API

// Analysis History (populated dynamically)
let historyStore = [];

// Application State
const state = {
  currentView: "home",
  activeTab: "text", // 'text' | 'file'
  uploadedFile: null,
  currentQuery: "",
  analysisRunning: false,
  analysisProgress: 0,
  activeStageIndex: 0
};

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

  if (!state.uploadedFile && !queryText) {
    alert("Please enter tender text or upload a PDF.");
    return;
  }

  if (state.uploadedFile) {
    state.currentQuery = `Procurement Tender: ${state.uploadedFile.name}`;
  } else if (queryText) {
    state.currentQuery = queryText;
  }

  // Navigate to Loading Processing Screen
  navigateTo("loading");
  runLoadingSimulationUI();

  // Make the actual API call
  try {
    const formData = new FormData();
    if (state.uploadedFile) {
      formData.append("file", state.uploadedFile);
    } else {
      formData.append("text", queryText);
    }

    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
      headers: {
        'X-API-Key': 'development_key', 'Bypass-Tunnel-Reminder': 'true'
      }
    });

    if (!response.ok) {
      let errStr = "The request could not be processed. Please try again.";
      try {
        const errJson = await response.json();
        if (errJson.error === "DocumentExtractionError" && state.uploadedFile) {
          errStr = "This file could not be analyzed. Please upload a text-based PDF.";
        } else if (errJson.message) {
          errStr = errJson.message;
        }
      } catch (e) {}
      throw new Error(errStr);
    }

    const data = await response.json();
    window._lastAnalysisData = data;
    
    state.analysisRunning = false;
    addToHistory(state.currentQuery);
    populateResultsData(state.currentQuery, data);
    navigateTo("results");
  } catch (error) {
    state.analysisRunning = false;
    console.error("Backend API Error:", error);
    alert(error.message.includes("fetch") ? "Unable to reach the analysis server. Please check that the backend is running." : error.message);
    navigateTo("home");
  }
}

function runLoadingSimulationUI() {
  state.analysisRunning = true;
  state.analysisProgress = 0;
  state.activeStageIndex = 0;

  const circleFill = document.getElementById("circleFill");
  const circlePct = document.getElementById("circlePercentage");
  
  // Just visually rotate a spinner while waiting for API
  let currentPct = 0;
  const timer = setInterval(() => {
    if (!state.analysisRunning) {
      clearInterval(timer);
      return;
    }
    currentPct = (currentPct + 1) % 99;
    if (circleFill) circleFill.style.strokeDasharray = `${currentPct}, 100`;
    if (circlePct) circlePct.innerText = `${currentPct}%`;
  }, 100);
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

// Populate Results View
function populateResultsData(query, apiData = null) {
  const queryBadge = document.getElementById("resultsQueryBadge");
  if (queryBadge) {
    queryBadge.innerText = query.length > 55 ? `${query.substring(0, 52)}...` : query;
  }

  const prodVal = document.getElementById("underProdVal");
  const appVal = document.getElementById("underAppVal");
  const tagCloud = document.getElementById("underTagCloud");

  let standardsFound = 0;
  let relatedStandards = 0;
  let versionStatus = "NOT VERIFIED";
  let certification = "NOT VERIFIED";

  if (apiData && apiData.requirements && apiData.requirements.length > 0) {
    const req = apiData.requirements[0];
    if (prodVal) prodVal.innerText = req.product || "NOT VERIFIED";
    if (appVal) appVal.innerText = req.application || req.category || "NOT VERIFIED";
    if (tagCloud) {
      tagCloud.innerHTML = "";
      if (req.parameters) {
        Object.entries(req.parameters).forEach(([k, v]) => {
          tagCloud.innerHTML += `<span class="spec-tag">${k}: ${v}</span>`;
        });
      }
    }
    
    let standardsList = [];
    if (apiData.recommendations && apiData.recommendations[req.requirement_id]) {
      standardsList = apiData.recommendations[req.requirement_id].map(rec => ({
        code: rec.is_number,
        title: rec.title,
        status: rec.compliance?.standard_status || "NOT VERIFIED",
        relevance: Math.round(rec.system_match_score * 100),
        description: `QCO Applicable: ${rec.compliance?.qco_applicable === true ? 'Yes' : 'No'} | Cert: ${rec.compliance?.certification_required === true ? 'Mandatory' : 'Voluntary / Not Verified'}`,
        whyMatches: rec.match_reasons || [],
        normativeReferences: rec.compliance?.normative_references || [],
        rawRec: rec // save for modal
      }));
    }

    standardsFound = standardsList.length;

    // Build related standards graph dynamically
    const graphContainer = document.getElementById("dynamicStandardsGraph");
    if (graphContainer) {
      if (standardsList.length === 0) {
        // CASE 3: No recommendation
        graphContainer.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--secondary-text);">No verified recommendation available for relationship analysis.</div>`;
      } else {
        let graphHtml = "";
        let hasEdges = false;
        
        apiData.recommendations[req.requirement_id]?.forEach(rec => {
          if (rec.compliance?.normative_relationships?.length > 0) {
            hasEdges = true;
            
            // Group edges by type
            const tests = [];
            const components = [];
            const related = [];
            
            rec.compliance.normative_relationships.forEach(edge => {
              relatedStandards++;
              const type = edge.relationship_type || "";
              if (type.includes("TEST")) {
                tests.push(edge);
              } else if (type.includes("COMPONENT") || type.includes("MATERIAL")) {
                components.push(edge);
              } else {
                related.push(edge);
              }
            });
            
            graphHtml += `
            <div style="display: flex; flex-direction: column; align-items: center; width: 100%; margin-bottom: 30px;">
              <div class="node-box primary" style="background: var(--primary-green); color: white; padding: 12px 20px; border-radius: 8px; font-weight: 600; box-shadow: 0 4px 12px rgba(11, 79, 108, 0.2); text-align: center;">
                ${rec.is_number}
                <div style="font-size: 0.75rem; opacity: 0.9; margin-top: 4px; font-weight: 400;">Main Recommended Standard</div>
              </div>
              
              <div style="width: 2px; height: 30px; background: #cbd5e1;"></div>
              
              <div style="background: #f1f5f9; padding: 6px 16px; border-radius: 16px; font-size: 0.8rem; font-weight: 500; color: #475569; margin-bottom: 0;">
                Verified Normative Relationships
              </div>
              
              <div style="width: 2px; height: 30px; background: #cbd5e1;"></div>
              
              <div style="display: flex; width: 100%; min-width: 600px; max-width: 900px; position: relative;">
                <div style="position: absolute; top: 0; left: 16.66%; right: 16.66%; height: 2px; background: #cbd5e1;"></div>
                
                <div style="flex: 1; display: flex; flex-direction: column; align-items: center; padding: 0 10px;">
                  <div style="width: 2px; height: 20px; background: #cbd5e1;"></div>
                  <div style="background: #eff6ff; color: #1d4ed8; font-size: 0.8rem; font-weight: 600; padding: 6px 0; width: 100%; text-align: center; border-radius: 6px; margin-bottom: 12px; border: 1px solid #bfdbfe;">Test Method</div>
                  ${tests.map(e => `
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; width: 100%; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                      <div style="font-weight: 600; color: #334155; font-size: 0.85rem;">${e.to_is}</div>
                      <div style="font-size: 0.7rem; color: #64748b; margin-top: 4px; line-height: 1.3;">${e.to_title || ''}</div>
                    </div>
                  `).join('')}
                  ${tests.length === 0 ? `<div style="font-size: 0.75rem; color: #94a3b8; font-style: italic;">None identified</div>` : ''}
                </div>
                
                <div style="flex: 1; display: flex; flex-direction: column; align-items: center; padding: 0 10px;">
                  <div style="width: 2px; height: 20px; background: #cbd5e1;"></div>
                  <div style="background: #fdf4ff; color: #a21caf; font-size: 0.8rem; font-weight: 600; padding: 6px 0; width: 100%; text-align: center; border-radius: 6px; margin-bottom: 12px; border: 1px solid #fbcfe8;">Component</div>
                  ${components.map(e => `
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; width: 100%; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                      <div style="font-weight: 600; color: #334155; font-size: 0.85rem;">${e.to_is}</div>
                      <div style="font-size: 0.7rem; color: #64748b; margin-top: 4px; line-height: 1.3;">${e.to_title || ''}</div>
                    </div>
                  `).join('')}
                  ${components.length === 0 ? `<div style="font-size: 0.75rem; color: #94a3b8; font-style: italic;">None identified</div>` : ''}
                </div>
                
                <div style="flex: 1; display: flex; flex-direction: column; align-items: center; padding: 0 10px;">
                  <div style="width: 2px; height: 20px; background: #cbd5e1;"></div>
                  <div style="background: #f0fdf4; color: #15803d; font-size: 0.8rem; font-weight: 600; padding: 6px 0; width: 100%; text-align: center; border-radius: 6px; margin-bottom: 12px; border: 1px solid #bbf7d0;">Related</div>
                  ${related.map(e => `
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; width: 100%; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                      <div style="font-weight: 600; color: #334155; font-size: 0.85rem;">${e.to_is}</div>
                      <div style="font-size: 0.7rem; color: #64748b; margin-top: 4px; line-height: 1.3;">${e.to_title || ''}</div>
                    </div>
                  `).join('')}
                  ${related.length === 0 ? `<div style="font-size: 0.75rem; color: #94a3b8; font-style: italic;">None identified</div>` : ''}
                </div>
              </div>
            </div>`;
          }
        });
        
        if (!hasEdges) {
          // CASE 2: Recommendation verified but no relationship evidence
          graphContainer.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--secondary-text);">NOT VERIFIED — no verified normative relationships found.</div>`;
        } else {
          // CASE 1: Relationships verified -> show graph
          graphContainer.innerHTML = graphHtml;
        }
      }
    }

    if (standardsList.length > 0) {
      versionStatus = standardsList[0].status;
      certification = standardsList[0].rawRec.compliance?.certification_required ? "Applicable" : "NOT VERIFIED";
    }
    
    renderRecommendedCards(standardsList);
    
    // Add empty state if no standards
    if (standardsList.length === 0) {
      const container = document.getElementById("recommendedCardsContainer");
      if (container) {
        container.innerHTML = `<div style="padding: 20px; background: #fff3cd; color: #664d03; border: 1px solid #ffe69c; border-radius: 8px;">No sufficiently verified BIS recommendation found in the current local knowledge base. Human verification required.</div>`;
      }
    }

    const versionTimelineContainer = document.getElementById("versionTimelineContainer");
    if (versionTimelineContainer) {
      if (standardsList.length > 0 && standardsList[0].status !== "NOT VERIFIED") {
        versionTimelineContainer.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--secondary-text);">Timeline data available in detailed view. Currently Active.</div>`;
      } else {
        versionTimelineContainer.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--secondary-text);">NOT VERIFIED - version/amendment history is unavailable in current local knowledge base.</div>`;
      }
    }

    const certificationContainer = document.getElementById("certificationGuidanceContainer");
    if (certificationContainer) {
      if (standardsList.length > 0 && standardsList[0].rawRec && standardsList[0].rawRec.compliance) {
        let isMandatory = standardsList[0].rawRec.compliance.certification_required === true;
        let qcoDetails = standardsList[0].rawRec.compliance.qco_details || [];
        if (isMandatory || qcoDetails.length > 0) {
          certificationContainer.innerHTML = `<div class="cert-item-card">
              <div class="cert-name">BIS Product Certification / QCO</div>
              <div class="cert-status applicable"> Applicable</div>
            </div>
            <div class="cert-disclaimer">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
              Local QCO mapping indicates certification may be required. Verify current notification, effective date, exceptions, and procurement applicability before publication.</div>`;
        } else {
          certificationContainer.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--secondary-text);">NOT VERIFIED - No mandatory certification identified.</div>`;
        }
      } else {
        certificationContainer.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--secondary-text);">NOT VERIFIED - No mandatory certification identified.</div>`;
      }
    }

    renderGapsAndFixes(apiData);
  } else {
    if (prodVal) prodVal.innerText = "NOT VERIFIED";
    if (appVal) appVal.innerText = "NOT VERIFIED";
    if (tagCloud) tagCloud.innerHTML = "";
    
    const graphContainer = document.getElementById("dynamicStandardsGraph");
    if (graphContainer) graphContainer.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--secondary-text);">No verified recommendation available for relationship analysis.</div>`;
    
    const container = document.getElementById("recommendedCardsContainer");
    if (container) {
        container.innerHTML = `<div style="padding: 20px; background: #fff3cd; color: #664d03; border: 1px solid #ffe69c; border-radius: 8px;">No sufficiently verified BIS recommendation found in the current local knowledge base. Human verification required.</div>`;
    }
    renderGapsAndFixes(null);
  }

  // Update metrics
  const m1 = document.getElementById("metricStandardsFound");
  const m2 = document.getElementById("metricRelatedStandards");
  const m3 = document.getElementById("metricVersionStatus");
  const m4 = document.getElementById("metricCertification");
  if (m1) m1.innerText = standardsFound;
  if (m2) m2.innerText = relatedStandards;
  if (m3) m3.innerText = versionStatus;
  if (m4) m4.innerText = certification;
} 

function renderGapsAndFixes(apiData) {
  let container = document.getElementById("dynamicGapsContainer");
  if (!container) {
    // Create it if it doesn't exist
    container = document.createElement("div");
    container.id = "dynamicGapsContainer";
    container.className = "result-section";
    const targetNode = document.getElementById("recommendedCardsContainer");
    if (targetNode && targetNode.parentNode) {
      targetNode.parentNode.parentNode.insertBefore(container, targetNode.parentNode.nextSibling);
    }
  }

  if (!apiData || (!apiData.gaps?.length && !apiData.fix_suggestions?.length)) {
    container.innerHTML = `
      <div class="section-header">
        <h2 class="section-title">Gap Analysis & Fixes</h2>
        <div class="section-subtext">No gap findings returned for this analysis.</div>
      </div>
    `;
    return;
  }

  let html = `
    <div class="section-header">
      <h2 class="section-title" style="color: var(--warning-color, #d97706)">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
        Gap Analysis & Fix Suggestions
      </h2>
      <div class="section-subtext">Suggested Draft for Human Review</div>
    </div>
  `;

  // Render Gaps
  if (apiData.gaps?.length) {
    apiData.gaps.forEach(gap => {
      html += `
        <div style="background: #fff3cd; border: 1px solid #ffe69c; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
          <strong style="color: #664d03; display: block; margin-bottom: 4px;">Gap: ${gap.gap_type} (Severity: ${gap.severity})</strong>
          <p style="font-size: 0.9rem; color: #664d03; margin-bottom: 8px;">${gap.message}</p>
          <div style="font-size: 0.8rem; color: #664d03;"><em>Related Standards: ${gap.related_standards?.join(", ") || "NOT VERIFIED"}</em></div>
        </div>
      `;
    });
  }

  // Render Fixes
  if (apiData.fix_suggestions?.length) {
    apiData.fix_suggestions.forEach(fix => {
      html += `
        <div style="background: #e2f0d9; border: 1px solid #c5e0b4; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
          <strong style="color: #385723; display: block; margin-bottom: 4px;">Suggested Revision</strong>
          <p style="font-size: 0.9rem; color: #385723; margin-bottom: 8px;"><strong>Original:</strong> "${fix.original_requirement}"</p>
          <p style="font-size: 0.95rem; font-weight: 600; color: #385723; margin-bottom: 8px;"><strong>Draft:</strong> "${fix.suggested_revision}"</p>
          <div style="font-size: 0.8rem; color: #385723;"><em>Reason: ${fix.reason} (Standard: ${fix.supporting_standard || "NOT VERIFIED"})</em></div>
        </div>
      `;
    });
  }

  container.innerHTML = html;
}

// Render Top 3 Recommendation Cards
function renderRecommendedCards(standardsList) {
  const container = document.getElementById("recommendedCardsContainer");
  if (!container) return;

  container.innerHTML = standardsList.slice(0, 3).map((std, idx) => `
    <div class="standard-recommendation-card">
      <div class="standard-top-row">
        <div>
          <span class="standard-number-badge">${std.code}</span>
          <h3 class="standard-title">${std.title}</h3>
        </div>
        <div class="standard-badges-right">
          <span class="relevance-score-badge">System Match Score: ${std.relevance}%</span>
          <span class="status-live-badge"><span class="status-live-dot"></span> </span>
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
          Semantic System Match Score: ${std.relevance}%
        </div>
        <ul class="why-checklist">
          ${std.whyMatches.map(item => `
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
  `).join("");
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
  let standard = null;
  // If we have live data
  if (window._lastAnalysisData) {
     const allRecs = Object.values(window._lastAnalysisData.recommendations || {}).flat();
     const rec = allRecs.find(r => r.is_number === code);
     if (rec) {
       standard = {
         code: rec.is_number,
         title: rec.title,
         status: rec.compliance?.standard_status || "NOT VERIFIED",
         relevance: Math.round(rec.system_match_score * 100),
         description: `Confidence: ${rec.confidence}`,
         certification: rec.compliance?.certification_required === true ? "Mandatory" : "Voluntary / Not Verified",
         normativeReferences: rec.compliance?.normative_references || [],
         amendments: (rec.compliance?.amendments || []).map(a => ({ year: 'N/A', label: a }))
       };
     }
  }
  
  if (!standard) {
    standard = state.activeStandardsMap[code] || { code: code, title: "Standard details not available", status: "NOT VERIFIED", relevance: 0, description: "No detailed information available in current analysis.", whyMatches: [], normativeReferences: [], certification: "NOT VERIFIED", amendments: [] };
  }

  const modal = document.getElementById("standardDetailsModal");
  const modalBody = document.getElementById("modalBodyContent");

  if (!modal || !modalBody) return;

  modalBody.innerHTML = `
    <div style="margin-bottom: 24px;">
      <h2 style="font-size: 1.4rem; color: var(--navy-text); margin-bottom: 8px;">${standard.code}</h2>
      <p style="font-size: 1rem; color: var(--secondary-text); font-weight: 500;">${standard.title}</p>
      <div style="display: flex; gap: 12px; margin-top: 12px;">
        <span class="status-live-badge"><span class="status-live-dot"></span> ${standard.status}</span>
        <span class="relevance-score-badge">System Match Score: ${standard.relevance}%</span>
      </div>
    </div>

    <div style="margin-bottom: 20px;">
      <h4 style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: var(--secondary-text); margin-bottom: 6px;">Compliance Rules</h4>
      <p style="font-size: 0.95rem; color: var(--primary-text); background: var(--bg-color); padding: 12px; border-radius: 6px; border-left: 4px solid var(--primary-green);">
        ${standard.certification || "NOT VERIFIED"}
      </p>
    </div>

    <div style="margin-bottom: 20px;">
      <h4 style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: var(--secondary-text); margin-bottom: 6px;">Normative Cross-References</h4>
      <div style="display: flex; gap: 8px; flex-wrap: wrap;">
        ${(standard.normativeReferences || []).map(ref => `<span class="spec-tag">${ref}</span>`).join("")}
        ${!(standard.normativeReferences?.length) ? '<span class="spec-tag">None Available</span>' : ''}
      </div>
    </div>

    <div>
      <h4 style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: var(--secondary-text); margin-bottom: 6px;">Amendment History</h4>
      <div style="display: flex; flex-direction: column; gap: 8px; border: 1px solid var(--border-color); border-radius: 6px; padding: 12px;">
        ${(standard.amendments || []).map(am => `
          <div style="display: flex; gap: 16px; font-size: 0.9rem;">
            <span style="font-weight: 600; color: var(--navy-text); min-width: 40px;">${am.year || 'Ver.'}</span>
            <span style="color: var(--secondary-text);">${am.label}</span>
          </div>
        `).join("")}
        ${!(standard.amendments?.length) ? '<div style="font-size: 0.9rem;">NOT VERIFIED</div>' : ''}
      </div>
    </div>
  `;

  modal.classList.add("active");
}

function closeStandardModal() {
  const modal = document.getElementById("standardDetailsModal");
  if (modal) modal.classList.remove("active");
}

// Standards Knowledge Base Catalog View
async function renderStandardsCatalog() {
  const tableBody = document.getElementById("standardsTableBody");
  if (!tableBody) return;
  const searchInput = document.getElementById("standardsSearchInput");
  const query = searchInput && searchInput.value.trim() !== "" ? searchInput.value : "standard";
  
  tableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 24px;">Loading from API...</td></tr>`;
  try {
    const res = await fetch(`${API_BASE_URL}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Bypass-Tunnel-Reminder": "true" },
      body: JSON.stringify({ query: query, top_k: 15 })
    });
    const data = await res.json();
    if (!data.results || data.results.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--secondary-text); padding: 24px;">No Indian Standards found matching your criteria.</td></tr>`;
      return;
    }
    tableBody.innerHTML = data.results.map(rec => `
      <tr>
        <td style="font-weight: 700; color: var(--deep-green);">${rec.is_number}</td>
        <td>
          <div style="font-weight: 600;">${rec.title}</div>
          <div style="font-size: 0.75rem; color: var(--secondary-text);">System Match Score: ${Math.round(rec.system_match_score * 100)}%</div>
        </td>
        <td><span class="spec-tag">${rec.compliance?.qco_applicable ? 'QCO Applicable' : 'Standard'}</span></td>
        <td><span class="status-live-badge"><span class="status-live-dot"></span> ${rec.compliance?.standard_status || 'NOT VERIFIED'}</span></td>
        <td>
          <button class="btn-outline" style="padding: 4px 10px; font-size: 0.775rem;" onclick="openStandardModal('${rec.is_number}')">
            Details
          </button>
        </td>
      </tr>
    `).join("");
    
    data.results.forEach(rec => {
      state.activeStandardsMap[rec.is_number] = {
        code: rec.is_number,
        title: rec.title,
        status: rec.compliance?.standard_status || "NOT VERIFIED",
        relevance: Math.round(rec.system_match_score * 100),
        description: `Confidence: ${rec.confidence}`,
        certification: rec.compliance?.certification_required ? "Mandatory" : "Voluntary / Not Verified",
        normativeReferences: rec.compliance?.normative_references || [],
        amendments: (rec.compliance?.amendments || []).map(a => ({ year: 'N/A', label: a }))
      };
    });
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red; padding: 24px;">Failed to load catalog from API.</td></tr>`;
  }
}

// History Page Table
function renderHistoryTable() {
  const tbody = document.getElementById("historyTableBody");
  if (!tbody) return;

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
    date: "20 Sep 2026",
    standardsFound: 8,
    status: "Completed",
    category: "General Procurement"
  });
}

function viewHistoryItem(index) {
  const item = historyStore[index];
  if (item) {
    populateResultsData(item.requirement);
    navigateTo("results");
  }
}

// Export Report Printable View
function exportProcurementReport() {
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


