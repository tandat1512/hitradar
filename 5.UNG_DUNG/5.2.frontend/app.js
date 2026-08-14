/**
 * HitRadar Pro - Phòng Thí Nghiệm & Bản Đồ Không Gian Âm Nhạc Spotify AI
 * Full Features: Galaxy Map, EDA Lab, Sci-Fi Radar HUD, Mood Quadrant, Web Audio Synth
 */

const API_BASE_KEY = "hitradar.apiBase";
const defaultApiBase = new URLSearchParams(window.location.search).get("api") || "http://127.0.0.1:8000";
const apiBaseInput = document.querySelector("#apiBaseInput");
const apiStatus = document.querySelector("#apiStatus");
const apiStatusText = document.querySelector("#apiStatusText");
const toast = document.querySelector("#toast");
const healthJson = document.querySelector("#healthJson");
const insightApi = document.querySelector("#insightApi");
const insightApiDetail = document.querySelector("#insightApiDetail");

// Presets âm nhạc mẫu
const musicPresets = {
  pop: {
    duration_min: 3.2,
    explicit: false,
    release_year: 2020,
    release_month: 7,
    release_precision: "day",
    danceability: 0.76,
    energy: 0.72,
    key: 0, // C (Đô)
    loudness: -5.5,
    mode: 1, // Major (Trưởng)
    speechiness: 0.06,
    acousticness: 0.12,
    instrumentalness: 0.00,
    liveness: 0.14,
    valence: 0.68,
    tempo: 124,
    time_signature: 4,
  },
  edm: {
    duration_min: 3.6,
    explicit: false,
    release_year: 2020,
    release_month: 8,
    release_precision: "day",
    danceability: 0.82,
    energy: 0.91,
    key: 5, // F (Fa)
    loudness: -3.8,
    mode: 0, // Minor (Thứ)
    speechiness: 0.09,
    acousticness: 0.03,
    instrumentalness: 0.45,
    liveness: 0.28,
    valence: 0.52,
    tempo: 128,
    time_signature: 4,
  },
  synthwave: {
    duration_min: 3.8,
    explicit: false,
    release_year: 2020,
    release_month: 6,
    release_precision: "day",
    danceability: 0.72,
    energy: 0.85,
    key: 7, // G (Sol)
    loudness: -5.0,
    mode: 0, // Minor (Thứ)
    speechiness: 0.05,
    acousticness: 0.02,
    instrumentalness: 0.60,
    liveness: 0.15,
    valence: 0.55,
    tempo: 128,
    time_signature: 4,
  },
  ballad: {
    duration_min: 4.1,
    explicit: false,
    release_year: 2019,
    release_month: 11,
    release_precision: "day",
    danceability: 0.42,
    energy: 0.35,
    key: 2, // D (Rê)
    loudness: -10.2,
    mode: 1, // Major (Trưởng)
    speechiness: 0.04,
    acousticness: 0.78,
    instrumentalness: 0.02,
    liveness: 0.10,
    valence: 0.28,
    tempo: 78,
    time_signature: 4,
  },
  lofi: {
    duration_min: 2.5,
    explicit: false,
    release_year: 2020,
    release_month: 5,
    release_precision: "day",
    danceability: 0.62,
    energy: 0.40,
    key: 9, // A (La)
    loudness: -11.0,
    mode: 0, // Minor (Thứ)
    speechiness: 0.05,
    acousticness: 0.65,
    instrumentalness: 0.85,
    liveness: 0.11,
    valence: 0.45,
    tempo: 85,
    time_signature: 4,
  },
  rock: {
    duration_min: 3.8,
    explicit: true,
    release_year: 2018,
    release_month: 9,
    release_precision: "day",
    danceability: 0.50,
    energy: 0.88,
    key: 4, // E (Mi)
    loudness: -4.2,
    mode: 1, // Major (Trưởng)
    speechiness: 0.08,
    acousticness: 0.05,
    instrumentalness: 0.15,
    liveness: 0.22,
    valence: 0.60,
    tempo: 142,
    time_signature: 4,
  },
};

apiBaseInput.value = localStorage.getItem(API_BASE_KEY) || defaultApiBase;

function apiBase() {
  return apiBaseInput.value.trim().replace(/\/+$/, "");
}

function showToast(message, isSuccess = true) {
  toast.innerHTML = `${isSuccess ? "✅" : "⚠️"} ${message}`;
  toast.classList.add("is-visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("is-visible"), 3500);
}

function setBusy(button, busy, label) {
  if (!button) return;
  if (!button.dataset.idleLabel) button.dataset.idleLabel = button.innerHTML;
  button.disabled = busy;
  button.innerHTML = busy ? `⏳ ${label}` : button.dataset.idleLabel;
}

function numberValue(form, name) {
  return Number(new FormData(form).get(name));
}

function boolValue(form, name) {
  return new FormData(form).get(name) === "on";
}

function predictionPayload(form) {
  const data = new FormData(form);
  return {
    duration_min: numberValue(form, "duration_min"),
    explicit: boolValue(form, "explicit"),
    release_year: numberValue(form, "release_year"),
    release_month: numberValue(form, "release_month"),
    release_precision: data.get("release_precision"),
    danceability: numberValue(form, "danceability"),
    energy: numberValue(form, "energy"),
    key: numberValue(form, "key"),
    loudness: numberValue(form, "loudness"),
    mode: numberValue(form, "mode"),
    speechiness: numberValue(form, "speechiness"),
    acousticness: numberValue(form, "acousticness"),
    instrumentalness: numberValue(form, "instrumentalness"),
    liveness: numberValue(form, "liveness"),
    valence: numberValue(form, "valence"),
    tempo: numberValue(form, "tempo"),
    time_signature: numberValue(form, "time_signature"),
  };
}

function clusterPayload(form) {
  return {
    duration_min: numberValue(form, "duration_min"),
    danceability: numberValue(form, "danceability"),
    energy: numberValue(form, "energy"),
    loudness: numberValue(form, "loudness"),
    speechiness: numberValue(form, "speechiness"),
    acousticness: numberValue(form, "acousticness"),
    instrumentalness: numberValue(form, "instrumentalness"),
    liveness: numberValue(form, "liveness"),
    valence: numberValue(form, "valence"),
    tempo: numberValue(form, "tempo"),
  };
}

async function requestJson(path, options = {}) {
  const response = await fetch(`${apiBase()}${path}`, {
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof payload.detail === "string" ? payload.detail : JSON.stringify(payload.detail || payload);
    throw new Error(detail || `Mã lỗi HTTP ${response.status}`);
  }
  return payload;
}

function renderMeta(container, rows) {
  container.innerHTML = rows
    .map(([label, value]) => `
      <div class="meta-item">
        <dt>${label}</dt>
        <dd>${value}</dd>
      </div>
    `)
    .join("");
}

// Hiệu ứng đếm số mượt mà (Animated Score Counter)
function animateScore(targetScore) {
  const scoreValue = document.querySelector("#scoreValue");
  const scoreRing = document.querySelector("#scoreRing");
  const clamped = Math.max(0, Math.min(100, Number(targetScore)));
  
  const start = Number(scoreValue.textContent) || 0;
  const duration = 1000;
  const startTime = performance.now();

  function updateNumber(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeProgress = 1 - Math.pow(1 - progress, 3);
    const currentVal = start + (clamped - start) * easeProgress;
    scoreValue.textContent = currentVal.toFixed(1);

    if (progress < 1) {
      requestAnimationFrame(updateNumber);
    } else {
      scoreValue.textContent = clamped.toFixed(1);
    }
  }
  requestAnimationFrame(updateNumber);

  const offset = 578 - (578 * clamped) / 100;
  scoreRing.style.strokeDashoffset = `${offset}`;

  if (clamped >= 70) {
    scoreRing.style.stroke = "var(--spotify-green)";
  } else if (clamped >= 50) {
    scoreRing.style.stroke = "var(--neon-amber)";
  } else if (clamped >= 30) {
    scoreRing.style.stroke = "var(--neon-cyan)";
  } else {
    scoreRing.style.stroke = "var(--neon-coral)";
  }
}

function updateTierBadge(tier) {
  const tierBadge = document.querySelector("#tierLabel");
  tierBadge.className = "tier-badge";
  
  const lower = String(tier).toLowerCase();
  if (lower.includes("high") || lower.includes("cao")) {
    tierBadge.textContent = "🌟 SIÊU PHẨM (High Tier)";
    tierBadge.classList.add("tier-high");
  } else if (lower.includes("medium") || lower.includes("trung")) {
    tierBadge.textContent = "🔥 TIỀM NĂNG (Medium Tier)";
    tierBadge.classList.add("tier-medium");
  } else if (lower.includes("emerging") || lower.includes("mới")) {
    tierBadge.textContent = "✨ MỚI NỔI (Emerging Tier)";
    tierBadge.classList.add("tier-emerging");
  } else {
    tierBadge.textContent = "🎵 KÉN NGƯỜI NGHE (Low Tier)";
    tierBadge.classList.add("tier-low");
  }
}

function updateRangeOutputs(root = document) {
  root.querySelectorAll('input[type="range"]').forEach((input) => {
    const output = input.parentElement.querySelector("output");
    if (output) {
      if (input.name === "n") {
        output.value = `${input.value} bài`;
      } else {
        output.value = input.step === "1" ? input.value : Number(input.value).toFixed(2);
      }
    }
  });
}

function fillForm(form, values) {
  Object.entries(values).forEach(([name, value]) => {
    const field = form.elements[name];
    if (!field) return;
    if (field.type === "checkbox") {
      field.checked = Boolean(value);
    } else {
      field.value = String(value);
    }
  });
  updateRangeOutputs(form);
  updateVisualReadout();
  updateTemporalWarning();
  drawMoodQuadrant();
}

function updateTemporalWarning() {
  const year = Number(document.querySelector("#releaseYearInput").value);
  document.querySelector("#temporalWarning").classList.toggle("is-hidden", year <= 2020);
}

function updateVisualReadout() {
  const predictForm = document.querySelector("#predictForm");
  if (!predictForm) return;
  const tempo = predictForm.elements.tempo.value;
  const energy = Math.round(Number(predictForm.elements.energy.value) * 100);
  const valence = Math.round(Number(predictForm.elements.valence.value) * 100);
  
  const tempoEl = document.querySelector("#readoutTempo");
  const energyEl = document.querySelector("#readoutEnergy");
  const moodEl = document.querySelector("#readoutMood");
  
  if (tempoEl) tempoEl.textContent = `⏱️ ${tempo} BPM`;
  if (energyEl) energyEl.textContent = `⚡ Năng lượng ${energy}%`;
  if (moodEl) moodEl.textContent = `🎭 Tích cực ${valence}%`;
}

// Kiểm tra sức khỏe hệ thống Backend API
async function checkHealth() {
  apiStatus.className = "api-status";
  apiStatusText.textContent = "Đang kiểm tra kết nối...";
  insightApi.textContent = "Đang kết nối...";
  insightApiDetail.textContent = "Đang gửi yêu cầu kiểm tra tới /health endpoint.";
  try {
    const payload = await requestJson("/health");
    const ready = payload.status === "ready" && payload.model_ready;
    apiStatus.classList.add(ready ? "is-ready" : "is-down");
    apiStatusText.textContent = ready ? "API Sẵn Sàng (Ready)" : "API Giảm Hiệu Năng";
    insightApi.textContent = ready ? "Hoạt Động Tốt" : "Cảnh Báo";
    insightApiDetail.textContent = `Mô hình: ${payload.model_ready ? "Đã sẵn sàng" : "Chưa tải"}, Phân cụm: ${payload.cluster_ready ? "Đã sẵn sàng" : "Chưa tải"}.`;
    healthJson.textContent = JSON.stringify(payload, null, 2);
  } catch (error) {
    apiStatus.classList.add("is-down");
    apiStatusText.textContent = "Mất Kết Nối API";
    insightApi.textContent = "Ngoại Tuyến (Offline)";
    insightApiDetail.textContent = `Lỗi: ${error.message}`;
    healthJson.textContent = `Không thể kết nối máy chủ API tại ${apiBase()}.\nLỗi chi tiết: ${error.message}`;
  }
}

// Xử lý chuyển đổi Tab (Navigation)
document.querySelectorAll(".nav-pill").forEach((button) => {
  button.addEventListener("click", () => {
    const view = button.dataset.view;
    document.querySelectorAll(".nav-pill").forEach((item) => item.classList.toggle("is-active", item === button));
    document.querySelectorAll("[data-view-panel]").forEach((panel) => {
      panel.classList.toggle("is-active", panel.dataset.viewPanel === view);
    });
    history.replaceState(null, "", `#${view}`);

    // Kích hoạt vẽ lại canvas khi tab hiển thị
    if (view === "galaxy") drawGalaxyMap();
    if (view === "eda") drawEdaCharts();
  });
});

// Xử lý thay đổi URL API
apiBaseInput.addEventListener("change", () => {
  localStorage.setItem(API_BASE_KEY, apiBase());
  checkHealth();
  showToast("Đã lưu địa chỉ Backend API mới.");
});

document.querySelector("#refreshHealth").addEventListener("click", () => {
  checkHealth();
  showToast("Đang kiểm tra lại máy chủ API...");
});

// Lắng nghe thay đổi slider
document.addEventListener("input", (event) => {
  if (event.target.matches('input[type="range"]')) {
    updateRangeOutputs(event.target.parentElement);
  }
  if (event.target.closest("#predictForm")) {
    updateVisualReadout();
    updateTemporalWarning();
    drawMoodQuadrant();
  }
});

// Nạp Preset theo phong cách nhạc
document.querySelectorAll(".preset-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".preset-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    const presetKey = btn.dataset.preset;
    if (musicPresets[presetKey]) {
      fillForm(document.querySelector("#predictForm"), musicPresets[presetKey]);
      showToast(`Đã áp dụng cấu hình mẫu: ${btn.textContent}`);
    }
  });
});

document.querySelector("#loadDemoPredict").addEventListener("click", () => {
  fillForm(document.querySelector("#predictForm"), musicPresets.pop);
  showToast("Đã khôi phục thông số mặc định (Pop).");
});

document.querySelector("#syncFromPredict").addEventListener("click", () => {
  const source = predictionPayload(document.querySelector("#predictForm"));
  fillForm(document.querySelector("#clusterForm"), source);
  showToast("Đã đồng bộ dấu vân tay âm thanh từ tab Studio!");
});

document.querySelector("#loadDemoTrack").addEventListener("click", () => {
  document.querySelector('#recommendForm [name="track_id"]').value = "00OQsMilg3NJQ365MDUnFJ";
  showToast("Đã nạp Spotify Track ID mẫu.");
});

// Xử lý gửi Form Dự đoán độ phổ biến
document.querySelector("#predictForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.submitter;
  setBusy(button, true, "Đang phân tích dữ liệu & tính điểm...");
  try {
    const result = await requestJson("/predict", {
      method: "POST",
      body: JSON.stringify(predictionPayload(event.currentTarget)),
    });
    
    animateScore(result.predicted_popularity);
    updateTierBadge(result.popularity_tier);

    let summaryText = "";
    if (result.temporal_extrapolation) {
      summaryText = `⚠️ ${result.support_note || "Năm phát hành vượt qua phạm vi huấn luyện chuẩn (2020), áp dụng ngoại suy xu thế."}`;
    } else {
      summaryText = "✨ Bài hát nằm trong phạm vi hỗ trợ chuẩn xác cao của mô hình XGBoost.";
    }
    document.querySelector("#predictionSummary").textContent = summaryText;

    renderMeta(document.querySelector("#predictionMeta"), [
      ["Thuật toán", result.model_name || "XGBoost Regressor"],
      ["Số đặc trưng", `${result.feature_count} Features`],
      ["Đặc trưng phái sinh", `${result.engineered_feature_count} Kỹ thuật`],
      ["Trạng thái", result.prediction_support_status === "SUPPORTED" ? "Chuẩn xác cao" : "Ngoại suy"],
    ]);

    showToast(`Dự đoán hoàn tất! Điểm số: ${Number(result.predicted_popularity).toFixed(1)}/100`);
  } catch (error) {
    showToast(`Dự đoán thất bại: ${error.message}`, false);
  } finally {
    setBusy(button, false);
  }
});

// Xử lý gửi Form Phân cụm âm thanh (K-Means)
document.querySelector("#clusterForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.submitter;
  setBusy(button, true, "Đang phân nhóm phong cách...");
  try {
    const result = await requestJson("/cluster", {
      method: "POST",
      body: JSON.stringify(clusterPayload(event.currentTarget)),
    });
    
    document.querySelector("#clusterValue").textContent = result.cluster;
    document.querySelector("#clusterTitle").textContent = `Cụm Phong Cách Số ${result.cluster} (k = ${result.chosen_k})`;
    document.querySelector("#clusterSummary").textContent = `Mô hình K-Means đã phân loại bài hát vào phân nhóm phong cách #${result.cluster} dựa trên 10 chỉ số âm học.`;
    
    renderMeta(document.querySelector("#clusterMeta"), [
      ["Số cụm tối ưu", `k = ${result.chosen_k} Cụm`],
      ["Số chiều đặc trưng", `${result.feature_count} Audio Features`],
      ["Mục tiêu phân loại", "Vibe & Giai điệu"],
      ["Sử dụng điểm Hot", "Không (Unbiased)"],
    ]);
    
    showToast(`Đã phân loại vào Cụm #${result.cluster}!`);
  } catch (error) {
    showToast(`Phân cụm thất bại: ${error.message}`, false);
  } finally {
    setBusy(button, false);
  }
});

// Xử lý gửi Form Gợi ý bài hát tương đồng
document.querySelector("#recommendForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.submitter;
  const data = new FormData(event.currentTarget);
  const trackId = encodeURIComponent(String(data.get("track_id")).trim());
  const n = Number(data.get("n"));
  
  setBusy(button, true, "Đang tính khoảng cách Cosine...");
  try {
    const result = await requestJson(`/recommend/${trackId}?n=${n}`);
    const count = result.recommendations ? result.recommendations.length : 0;
    document.querySelector("#recommendCount").textContent = `${count} bài tương đồng`;
    
    const resultsContainer = document.querySelector("#recommendResults");
    if (!result.recommendations || result.recommendations.length === 0) {
      resultsContainer.className = "empty-state";
      resultsContainer.textContent = "Không tìm thấy bài hát tương đồng phù hợp.";
      return;
    }

    resultsContainer.className = "recommend-list";
    resultsContainer.innerHTML = result.recommendations
      .map((item, idx) => {
        const similarityPct = (Number(item.cosine_similarity) * 100).toFixed(1);
        return `
          <div class="recommend-row">
            <div style="display: flex; align-items: center; gap: 12px;">
              <span style="font-weight: 800; color: var(--text-muted); font-size: 0.85rem; font-family: var(--font-mono);">#${idx + 1}</span>
              <span class="track-id">${item.track_id}</span>
            </div>
            <span class="similarity-badge">🎯 Độ tương đồng: ${similarityPct}%</span>
          </div>
        `;
      })
      .join("");

    showToast(`Đã tìm thấy ${count} bài hát có phong cách tương đồng nhất!`);
  } catch (error) {
    showToast(`Tìm kiếm thất bại: ${error.message}`, false);
  } finally {
    setBusy(button, false);
  }
});

/* ============================================================
   1. WEB AUDIO API SYNTHESIZER (NGHE THỬ VIBE ÂM SẮC)
   ============================================================ */
let audioCtx = null;
let isSynthPlaying = false;
let synthTimer = null;

const baseFreqMap = {
  0: 261.63, // C4
  1: 277.18, // C#4
  2: 293.66, // D4
  3: 311.13, // D#4
  4: 329.63, // E4
  5: 349.23, // F4
  6: 369.99, // F#4
  7: 392.00, // G4
  8: 415.30, // G#4
  9: 440.00, // A4
  10: 466.16,// A#4
  11: 493.88 // B4
};

function playSynthVibe() {
  const form = document.querySelector("#predictForm");
  const key = Number(form.elements.key.value) || 0;
  const mode = Number(form.elements.mode.value) || 1;
  const tempo = Number(form.elements.tempo.value) || 120;
  const energy = Number(form.elements.energy.value) || 0.7;
  const valence = Number(form.elements.valence.value) || 0.55;

  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioCtx.state === "suspended") {
    audioCtx.resume();
  }

  const baseFreq = baseFreqMap[key] || 261.63;
  // Major chord intervals: [0, 4, 7, 12] semitones; Minor chord: [0, 3, 7, 12]
  const semitones = mode === 1 ? [0, 4, 7, 12, 16] : [0, 3, 7, 12, 15];
  const notes = semitones.map((s) => baseFreq * Math.pow(2, s / 12));

  const noteDuration = (60 / tempo) * 0.5;
  const totalNotes = 8;
  const startTime = audioCtx.currentTime + 0.05;

  for (let i = 0; i < totalNotes; i++) {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    const filter = audioCtx.createBiquadFilter();

    // Chọn note arpeggio
    const noteIdx = i % notes.length;
    osc.type = energy > 0.6 ? "sawtooth" : "triangle";
    osc.frequency.setValueAtTime(notes[noteIdx], startTime + i * noteDuration);

    // Filter theo valence & energy
    filter.type = "lowpass";
    filter.frequency.setValueAtTime(800 + valence * 2500 + energy * 1500, startTime + i * noteDuration);

    // Gain envelope
    const nStart = startTime + i * noteDuration;
    gain.gain.setValueAtTime(0.001, nStart);
    gain.gain.exponentialRampToValueAtTime(0.25 * (0.5 + energy * 0.5), nStart + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, nStart + noteDuration * 0.95);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(audioCtx.destination);

    osc.start(nStart);
    osc.stop(nStart + noteDuration);
  }

  const playBtn = document.querySelector("#playSynthBtn");
  const synthText = document.querySelector("#synthText");
  const synthIcon = document.querySelector("#synthIcon");
  playBtn.classList.add("is-playing");
  synthIcon.textContent = "🔊";
  synthText.textContent = "Đang phát Vibe...";

  clearTimeout(synthTimer);
  synthTimer = setTimeout(() => {
    playBtn.classList.remove("is-playing");
    synthIcon.textContent = "▶️";
    synthText.textContent = "Nghe Thử Vibe Âm Sắc (Synth)";
  }, (totalNotes * noteDuration + 0.2) * 1000);
}

document.querySelector("#playSynthBtn").addEventListener("click", () => {
  playSynthVibe();
  showToast("Đang mô phỏng chuỗi hợp âm Synthesizer theo Key, Mode & BPM!");
});

/* ============================================================
   2. SCI-FI RADAR HUD CANVAS (VỚI TIA QUÉT XOAY TRÒN)
   ============================================================ */
let radarScanAngle = 0;
function drawRadarHUD() {
  const canvas = document.querySelector("#audioRadarCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const form = document.querySelector("#predictForm");
  if (!form) return;

  const features = [
    { name: "Bắt tai", val: Number(form.elements.danceability.value) },
    { name: "Năng lượng", val: Number(form.elements.energy.value) },
    { name: "Tươi vui", val: Number(form.elements.valence.value) },
    { name: "Mộc mạc", val: Number(form.elements.acousticness.value) },
    { name: "Nhạc cụ", val: Number(form.elements.instrumentalness.value) },
    { name: "Sân khấu", val: Number(form.elements.liveness.value) },
    { name: "Lời thoại", val: Number(form.elements.speechiness.value) },
  ];

  const width = canvas.width;
  const height = canvas.height;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(centerX, centerY) - 38;
  const count = features.length;
  const angleStep = (Math.PI * 2) / count;

  ctx.clearRect(0, 0, width, height);

  // 1. Vẽ các vòng lưới đa giác HUD
  const levels = 4;
  for (let l = 1; l <= levels; l++) {
    const levelRadius = (radius / levels) * l;
    ctx.beginPath();
    for (let i = 0; i < count; i++) {
      const angle = i * angleStep - Math.PI / 2;
      const x = centerX + levelRadius * Math.cos(angle);
      const y = centerY + levelRadius * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.strokeStyle = l === levels ? "rgba(0, 230, 153, 0.25)" : "rgba(255, 255, 255, 0.06)";
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  // 2. Tia quét Radar xoay tròn (Rotating Scanner Beam)
  ctx.save();
  ctx.translate(centerX, centerY);
  ctx.rotate(radarScanAngle);
  const scanGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, radius);
  scanGrad.addColorStop(0, "rgba(0, 230, 153, 0.4)");
  scanGrad.addColorStop(0.8, "rgba(0, 230, 153, 0.08)");
  scanGrad.addColorStop(1, "transparent");
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.arc(0, 0, radius, 0, 0.45);
  ctx.closePath();
  ctx.fillStyle = scanGrad;
  ctx.fill();
  ctx.restore();
  radarScanAngle += 0.028;

  // 3. Vẽ các trục nan hoa & Nhãn HUD
  for (let i = 0; i < count; i++) {
    const angle = i * angleStep - Math.PI / 2;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(x, y);
    ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
    ctx.stroke();

    const labelX = centerX + (radius + 24) * Math.cos(angle);
    const labelY = centerY + (radius + 20) * Math.sin(angle);
    ctx.fillStyle = "rgba(148, 163, 184, 0.9)";
    ctx.font = "600 11px 'Plus Jakarta Sans', sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(features[i].name, labelX, labelY);
  }

  // 4. Vẽ Đa giác Dữ liệu Đặc trưng Âm học
  ctx.beginPath();
  for (let i = 0; i < count; i++) {
    const angle = i * angleStep - Math.PI / 2;
    const valRadius = radius * Math.max(0.06, Math.min(1, features[i].val));
    const x = centerX + valRadius * Math.cos(angle);
    const y = centerY + valRadius * Math.sin(angle);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();

  ctx.fillStyle = "rgba(0, 230, 153, 0.2)";
  ctx.fill();
  ctx.strokeStyle = "#00e699";
  ctx.lineWidth = 2;
  ctx.stroke();

  // 5. Vẽ các Node tín hiệu phát sáng
  for (let i = 0; i < count; i++) {
    const angle = i * angleStep - Math.PI / 2;
    const valRadius = radius * Math.max(0.06, Math.min(1, features[i].val));
    const x = centerX + valRadius * Math.cos(angle);
    const y = centerY + valRadius * Math.sin(angle);
    ctx.beginPath();
    ctx.arc(x, y, 4.5, 0, Math.PI * 2);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    ctx.strokeStyle = "#00e699";
    ctx.lineWidth = 2;
    ctx.stroke();
  }

  requestAnimationFrame(drawRadarHUD);
}

/* ============================================================
   3. MOOD QUADRANT 2D MATRIX CANVAS
   ============================================================ */
function drawMoodQuadrant() {
  const canvas = document.querySelector("#moodQuadrantCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const form = document.querySelector("#predictForm");
  if (!form) return;

  const energy = Number(form.elements.energy.value);
  const valence = Number(form.elements.valence.value);

  const width = canvas.width;
  const height = canvas.height;
  const padding = 32;

  ctx.clearRect(0, 0, width, height);

  // Trục toạ độ giữa
  const midX = width / 2;
  const midY = height / 2;

  // 4 Vùng cảm xúc
  // Top-Right: Sôi Động & Tươi Vui
  ctx.fillStyle = "rgba(0, 230, 153, 0.05)";
  ctx.fillRect(midX, padding, midX - padding, midY - padding);

  // Bottom-Right: Thư Thái & Bình Yên
  ctx.fillStyle = "rgba(6, 182, 212, 0.05)";
  ctx.fillRect(midX, midY, midX - padding, midY - padding);

  // Bottom-Left: Trầm Tư & U Buồn
  ctx.fillStyle = "rgba(139, 92, 246, 0.05)";
  ctx.fillRect(padding, midY, midX - padding, midY - padding);

  // Top-Left: Bùng Nổ & Căng Thẳng
  ctx.fillStyle = "rgba(255, 77, 77, 0.05)";
  ctx.fillRect(padding, padding, midX - padding, midY - padding);

  // Vẽ trục X và Y
  ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(padding, midY);
  ctx.lineTo(width - padding, midY);
  ctx.moveTo(midX, padding);
  ctx.lineTo(midX, height - padding);
  ctx.stroke();

  // Nhãn 4 góc
  ctx.font = "700 11px 'Plus Jakarta Sans', sans-serif";
  ctx.fillStyle = "#00e699";
  ctx.fillText("⚡ Sôi Động / Happy", width - padding - 110, padding + 16);

  ctx.fillStyle = "#06b6d4";
  ctx.fillText("☕ Thư Thái / Chill", width - padding - 105, height - padding - 12);

  ctx.fillStyle = "#8b5cf6";
  ctx.fillText("🌧️ Trầm Tư / Melancholy", padding + 8, height - padding - 12);

  ctx.fillStyle = "#ff4d4d";
  ctx.fillText("🔥 Bùng Nổ / Intense", padding + 8, padding + 16);

  // Vị trí con trỏ bài hát hiện tại (X = Valence, Y = 1 - Energy)
  const markerX = padding + valence * (width - padding * 2);
  const markerY = padding + (1 - energy) * (height - padding * 2);

  // Vẽ vòng hào quang phát sáng
  ctx.beginPath();
  ctx.arc(markerX, markerY, 14, 0, Math.PI * 2);
  ctx.fillStyle = "rgba(0, 230, 153, 0.25)";
  ctx.fill();

  ctx.beginPath();
  ctx.arc(markerX, markerY, 6, 0, Math.PI * 2);
  ctx.fillStyle = "#00e699";
  ctx.fill();
  ctx.strokeStyle = "#ffffff";
  ctx.lineWidth = 2;
  ctx.stroke();

  // Cập nhật Badge Mood
  const moodBadge = document.querySelector("#currentMoodBadge");
  if (valence >= 0.5 && energy >= 0.5) {
    moodBadge.textContent = "⚡ Sôi Động & Tươi Vui (Happy Energy)";
  } else if (valence >= 0.5 && energy < 0.5) {
    moodBadge.textContent = "☕ Thư Thái & Bình Yên (Chill Vibe)";
  } else if (valence < 0.5 && energy < 0.5) {
    moodBadge.textContent = "🌧️ Trầm Tư & U Buồn (Melancholic)";
  } else {
    moodBadge.textContent = "🔥 Bùng Nổ & Dữ Dội (Intense Vibe)";
  }
}

/* ============================================================
   4. AUDIO GALAXY MAP CANVAS (BẢN ĐỒ THIÊN HÀ ÂM NHẠC 2D)
   ============================================================ */
let galaxyStars = [];
let hoveredNode = null;
let currentClusterFilter = "all";

function generateGalaxyData() {
  const stars = [];
  const clusterVibes = [
    { name: "Pop/Dance Vui Tươi", baseV: 0.7, baseE: 0.75, color: "#00e699", cluster: 0 },
    { name: "Acoustic/Ballad Trầm Lắng", baseV: 0.35, baseE: 0.35, color: "#8b5cf6", cluster: 1 },
    { name: "EDM/Rock Bùng Nổ", baseV: 0.55, baseE: 0.9, color: "#06b6d4", cluster: 2 },
  ];

  const songTitles = [
    "Midnight Groove", "Neon Dreams", "Acoustic Rain", "Electric Echo", "Sunset Avenue",
    "Cyber City", "Lofi Memory", "Golden Horizon", "Velvet Shadow", "Euphoria Pulse",
    "Starlight Drift", "Brave Heart", "Ocean Breeze", "Tokyo Lights", "Solitude Melody",
    "Quantum Jump", "Vintage Coffee", "Rave Dimension", "Silent Tears", "Summer Blossom"
  ];

  for (let i = 0; i < 300; i++) {
    const cl = clusterVibes[i % 3];
    const randAngle = Math.random() * Math.PI * 2;
    const randDist = Math.random() * 0.28;
    const valence = Math.max(0.05, Math.min(0.95, cl.baseV + Math.cos(randAngle) * randDist));
    const energy = Math.max(0.05, Math.min(0.95, cl.baseE + Math.sin(randAngle) * randDist));
    const title = songTitles[i % songTitles.length] + ` #${i + 1}`;

    stars.push({
      id: i,
      title: title,
      valence: valence,
      energy: energy,
      dance: (0.4 + Math.random() * 0.5).toFixed(2),
      popularity: Math.round(20 + Math.random() * 75),
      cluster: cl.cluster,
      color: cl.color,
      vibe: cl.name,
      size: 2 + Math.random() * 3,
      twinkle: Math.random() * Math.PI,
    });
  }
  return stars;
}

function drawGalaxyMap() {
  const canvas = document.querySelector("#galaxyCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const form = document.querySelector("#predictForm");

  const width = canvas.width;
  const height = canvas.height;
  const padding = 50;

  if (galaxyStars.length === 0) {
    galaxyStars = generateGalaxyData();
  }

  ctx.clearRect(0, 0, width, height);

  // Lưới không gian mờ
  ctx.strokeStyle = "rgba(255, 255, 255, 0.04)";
  ctx.lineWidth = 1;
  for (let x = padding; x < width - padding; x += 80) {
    ctx.beginPath();
    ctx.moveTo(x, padding);
    ctx.lineTo(x, height - padding);
    ctx.stroke();
  }
  for (let y = padding; y < height - padding; y += 60) {
    ctx.beginPath();
    ctx.moveTo(padding, y);
    ctx.lineTo(width - padding, y);
    ctx.stroke();
  }

  // Vẽ các vì sao bài hát
  galaxyStars.forEach((star) => {
    if (currentClusterFilter !== "all" && star.cluster !== Number(currentClusterFilter)) {
      return;
    }

    const x = padding + star.valence * (width - padding * 2);
    const y = padding + (1 - star.energy) * (height - padding * 2);

    star.twinkle += 0.03;
    const currentSize = star.size + Math.sin(star.twinkle) * 0.8;

    ctx.beginPath();
    ctx.arc(x, y, currentSize, 0, Math.PI * 2);
    ctx.fillStyle = star.color;
    ctx.shadowBlur = 8;
    ctx.shadowColor = star.color;
    ctx.fill();
    ctx.shadowBlur = 0;
  });

  // Vẽ Node bài hát hiện tại của người dùng
  if (form) {
    const userV = Number(form.elements.valence.value);
    const userE = Number(form.elements.energy.value);
    const ux = padding + userV * (width - padding * 2);
    const uy = padding + (1 - userE) * (height - padding * 2);

    // Vòng tròn phát sáng lớn
    ctx.beginPath();
    ctx.arc(ux, uy, 18, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(0, 230, 153, 0.25)";
    ctx.fill();

    ctx.beginPath();
    ctx.arc(ux, uy, 7, 0, Math.PI * 2);
    ctx.fillStyle = "#ffffff";
    ctx.shadowBlur = 16;
    ctx.shadowColor = "#00e699";
    ctx.fill();
    ctx.shadowBlur = 0;

    ctx.fillStyle = "#00e699";
    ctx.font = "800 12px 'Plus Jakarta Sans', sans-serif";
    ctx.fillText("📍 BÀI HÁT CỦA BẠN", ux + 14, uy + 4);
  }
}

// Xử lý tương tác chuột trên Galaxy Canvas
const galaxyCanvas = document.querySelector("#galaxyCanvas");
const galaxyNodeCard = document.querySelector("#galaxyNodeCard");

if (galaxyCanvas) {
  galaxyCanvas.addEventListener("mousemove", (e) => {
    const rect = galaxyCanvas.getBoundingClientRect();
    const scaleX = galaxyCanvas.width / rect.width;
    const scaleY = galaxyCanvas.height / rect.height;
    const mouseX = (e.clientX - rect.left) * scaleX;
    const mouseY = (e.clientY - rect.top) * scaleY;

    const padding = 50;
    const width = galaxyCanvas.width;
    const height = galaxyCanvas.height;

    let nearest = null;
    let minDist = 25;

    galaxyStars.forEach((star) => {
      if (currentClusterFilter !== "all" && star.cluster !== Number(currentClusterFilter)) return;
      const sx = padding + star.valence * (width - padding * 2);
      const sy = padding + (1 - star.energy) * (height - padding * 2);
      const dist = Math.hypot(mouseX - sx, mouseY - sy);
      if (dist < minDist) {
        minDist = dist;
        nearest = star;
      }
    });

    if (nearest) {
      galaxyNodeCard.classList.add("is-visible");
      document.querySelector("#nodeTrackName").textContent = `🎵 ${nearest.title}`;
      document.querySelector("#nodeVibe").textContent = nearest.vibe;
      document.querySelector("#nodeEnergy").textContent = `${Math.round(nearest.energy * 100)}%`;
      document.querySelector("#nodeDance").textContent = `${Math.round(nearest.dance * 100)}%`;
      document.querySelector("#nodePopularity").textContent = `${nearest.popularity}`;
    } else {
      galaxyNodeCard.classList.remove("is-visible");
    }
  });

  galaxyCanvas.addEventListener("mouseleave", () => {
    galaxyNodeCard.classList.remove("is-visible");
  });
}

document.querySelectorAll(".galaxy-chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    document.querySelectorAll(".galaxy-chip").forEach((c) => c.classList.remove("active"));
    chip.classList.add("active");
    currentClusterFilter = chip.dataset.clusterFilter;
    drawGalaxyMap();
  });
});

document.querySelector("#locateMyTrackBtn").addEventListener("click", () => {
  drawGalaxyMap();
  showToast("Đã định vị bài hát của bạn tại toạ độ năng lượng & cảm xúc hiện tại!");
});

/* ============================================================
   5. EDA CHARTS CANVAS (PHÒNG PHÂN TÍCH DỮ LIỆU & THẬP NIÊN)
   ============================================================ */
function drawEdaCharts() {
  drawDecadeTrendChart();
  drawEnergyDistChart();
  drawCorrelationChart();
}

function drawDecadeTrendChart() {
  const canvas = document.querySelector("#decadeTrendCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  const padding = 40;

  ctx.clearRect(0, 0, width, height);

  const decades = ["1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"];
  const loudness = [0.25, 0.35, 0.48, 0.65, 0.82, 0.88, 0.92]; // normalized
  const energy = [0.38, 0.48, 0.58, 0.62, 0.68, 0.70, 0.72];
  const danceability = [0.50, 0.52, 0.56, 0.58, 0.60, 0.65, 0.68];

  const stepX = (width - padding * 2) / (decades.length - 1);

  // Vẽ trục X
  ctx.strokeStyle = "rgba(255, 255, 255, 0.1)";
  ctx.beginPath();
  ctx.moveTo(padding, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.stroke();

  decades.forEach((d, i) => {
    const x = padding + i * stepX;
    ctx.fillStyle = "rgba(148, 163, 184, 0.8)";
    ctx.font = "600 10px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    ctx.fillText(d, x, height - padding + 18);
  });

  function drawLine(data, color, label) {
    ctx.beginPath();
    data.forEach((val, i) => {
      const x = padding + i * stepX;
      const y = height - padding - val * (height - padding * 2);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // Điểm nút
    data.forEach((val, i) => {
      const x = padding + i * stepX;
      const y = height - padding - val * (height - padding * 2);
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = "#06070a";
      ctx.fill();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.stroke();
    });
  }

  drawLine(loudness, "#ff4d4d", "Độ lớn Loudness");
  drawLine(energy, "#00e699", "Năng lượng Energy");
  drawLine(danceability, "#06b6d4", "Bắt tai Danceability");

  // Legend
  ctx.font = "600 11px 'Plus Jakarta Sans', sans-serif";
  ctx.fillStyle = "#ff4d4d";
  ctx.fillText("━ Loudness (dB)", padding + 20, padding - 12);
  ctx.fillStyle = "#00e699";
  ctx.fillText("━ Energy", padding + 140, padding - 12);
  ctx.fillStyle = "#06b6d4";
  ctx.fillText("━ Danceability", padding + 220, padding - 12);
}

function drawEnergyDistChart() {
  const canvas = document.querySelector("#energyDistCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  const padding = 40;

  ctx.clearRect(0, 0, width, height);

  const bins = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0];
  const popDensity = [15, 22, 34, 45, 62, 78, 92, 85, 60, 38]; // Điểm số phổ biến theo năng lượng

  const barWidth = (width - padding * 2) / bins.length - 8;

  bins.forEach((b, i) => {
    const x = padding + i * (barWidth + 8);
    const barH = (popDensity[i] / 100) * (height - padding * 2);
    const y = height - padding - barH;

    const isSweetSpot = b >= 0.6 && b <= 0.8;
    ctx.fillStyle = isSweetSpot ? "rgba(0, 230, 153, 0.75)" : "rgba(139, 92, 246, 0.45)";
    ctx.fillRect(x, y, barWidth, barH);

    ctx.fillStyle = "rgba(148, 163, 184, 0.8)";
    ctx.font = "600 10px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    ctx.fillText(`${b.toFixed(1)}`, x + barWidth / 2, height - padding + 16);
  });

  // Trục đáy
  ctx.strokeStyle = "rgba(255, 255, 255, 0.1)";
  ctx.beginPath();
  ctx.moveTo(padding, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.stroke();

  // Nhãn Sweet spot
  ctx.fillStyle = "#00e699";
  ctx.font = "700 11px 'Plus Jakarta Sans', sans-serif";
  ctx.fillText("🌟 Vùng Tối Ưu (Sweet Spot: 0.6 - 0.8)", width / 2 - 20, padding + 10);
}

function drawCorrelationChart() {
  const canvas = document.querySelector("#correlationCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  const padding = 50;

  ctx.clearRect(0, 0, width, height);

  const labels = ["Energy", "Loud", "Acoustic", "Dance", "Valence"];
  const matrix = [
    [1.00,  0.78, -0.72,  0.35,  0.42],
    [0.78,  1.00, -0.65,  0.38,  0.36],
    [-0.72,-0.65,  1.00, -0.28, -0.25],
    [0.35,  0.38, -0.28,  1.00,  0.54],
    [0.42,  0.36, -0.25,  0.54,  1.00]
  ];

  const size = (Math.min(width, height) - padding * 2) / labels.length;
  const startX = (width - size * labels.length) / 2 + 10;
  const startY = (height - size * labels.length) / 2 + 10;

  for (let r = 0; r < labels.length; r++) {
    for (let c = 0; c < labels.length; c++) {
      const val = matrix[r][c];
      const x = startX + c * size;
      const y = startY + r * size;

      if (val > 0) {
        ctx.fillStyle = `rgba(0, 230, 153, ${Math.abs(val) * 0.8})`;
      } else {
        ctx.fillStyle = `rgba(255, 77, 77, ${Math.abs(val) * 0.8})`;
      }
      ctx.fillRect(x + 2, y + 2, size - 4, size - 4);

      ctx.fillStyle = "#fff";
      ctx.font = "700 10px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(val.toFixed(2), x + size / 2, y + size / 2);
    }

    // Nhãn hàng & cột
    ctx.fillStyle = "rgba(148, 163, 184, 0.9)";
    ctx.font = "600 10px 'Plus Jakarta Sans', sans-serif";
    ctx.textAlign = "right";
    ctx.fillText(labels[r], startX - 8, startY + r * size + size / 2);
    ctx.textAlign = "center";
    ctx.fillText(labels[r], startX + r * size + size / 2, startY - 8);
  }
}

/* ============================================================
   6. VISUALIZER SÓNG ÂM THANH CANVAS
   ============================================================ */
function drawVisualizer() {
  const canvas = document.querySelector("#pulseCanvas");
  if (!canvas) return;
  const context = canvas.getContext("2d");
  const bars = 52;
  let phase = 0;

  function frame() {
    const width = canvas.width;
    const height = canvas.height;
    const form = document.querySelector("#predictForm");
    const energy = form ? Number(form.elements.energy.value) : 0.72;
    const valence = form ? Number(form.elements.valence.value) : 0.68;
    const tempo = form ? Number(form.elements.tempo.value) : 124;

    context.clearRect(0, 0, width, height);

    context.fillStyle = "#050608";
    context.fillRect(0, 0, width, height);

    for (let i = 0; i < bars; i++) {
      const x = (i / bars) * width;
      const barWidth = width / bars - 4;
      const wave = Math.sin(phase + i * 0.32) * 0.5 + 0.5;
      const barHeight = 20 + wave * 140 * (0.4 + energy * 0.8);
      
      const hue = 145 + i * 2.2 + valence * 50;
      const gradient = context.createLinearGradient(0, height - barHeight - 20, 0, height);
      gradient.addColorStop(0, `hsla(${hue}, 95%, 65%, 0.9)`);
      gradient.addColorStop(1, `hsla(${hue}, 85%, 40%, 0.2)`);

      context.fillStyle = gradient;
      context.beginPath();
      context.roundRect(x + 2, height - barHeight - 20, barWidth, barHeight, 3);
      context.fill();
    }

    context.strokeStyle = "#00e699";
    context.lineWidth = 2.5;
    context.shadowBlur = 10;
    context.shadowColor = "#00e699";
    context.beginPath();
    for (let x = 0; x < width; x += 6) {
      const y = height * 0.36 + Math.sin(phase * 1.5 + x * 0.02) * (14 + energy * 28);
      if (x === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    }
    context.stroke();
    context.shadowBlur = 0;

    phase += (tempo / 120) * 0.04;
    requestAnimationFrame(frame);
  }

  frame();
}

// Khởi tạo
const initialHash = window.location.hash.replace("#", "");
if (initialHash) {
  const target = document.querySelector(`.nav-pill[data-view="${initialHash}"]`);
  if (target) target.click();
}

updateRangeOutputs();
updateVisualReadout();
updateTemporalWarning();
checkHealth();
drawVisualizer();
drawRadarHUD();
drawMoodQuadrant();
