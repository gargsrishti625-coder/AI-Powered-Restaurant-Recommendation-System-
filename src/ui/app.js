/* AI Restaurant Recommender — frontend */
'use strict';

// ── DOM refs ─────────────────────────────────────────────────────────────────
const form       = document.getElementById('recommend-form');
const submitBtn  = document.getElementById('submit-btn');
const btnText    = submitBtn.querySelector('.btn-text');
const btnSpinner = document.getElementById('btn-spinner');

const ratingInput   = document.getElementById('min-rating');
const ratingDisplay = document.getElementById('rating-display');

// State panels (controlled via style.display, not the hidden attribute)
const stateEmpty   = document.getElementById('state-empty');
const stateLoading = document.getElementById('state-loading');
const stateError   = document.getElementById('state-error');
const stateResults = document.getElementById('state-results');
const errorTitle   = document.getElementById('error-title');
const errorText    = document.getElementById('error-text');
const resultsMeta  = document.getElementById('results-meta');
const resultsList  = document.getElementById('results-list');

// Multi-select refs
const msWrapper     = document.getElementById('ms-wrapper');
const msTrigger     = document.getElementById('ms-trigger');
const msTriggerText = document.getElementById('ms-trigger-text');
const msPanel       = document.getElementById('ms-panel');
const msSearch      = document.getElementById('ms-search');
const msList        = document.getElementById('ms-list');
const msChips       = document.getElementById('ms-chips');

// ── State ─────────────────────────────────────────────────────────────────────
let allCuisines      = [];
let selectedCuisines = new Set();
let panelOpen        = false;

// ── Show/hide panels ──────────────────────────────────────────────────────────
function showPanel(name) {
  stateEmpty.style.display   = name === 'empty'   ? 'flex' : 'none';
  stateLoading.style.display = name === 'loading' ? 'flex' : 'none';
  stateError.style.display   = name === 'error'   ? 'flex' : 'none';
  stateResults.style.display = name === 'results' ? 'block' : 'none';
}

function showError(title, text) {
  errorTitle.textContent = title;
  errorText.textContent  = text;
  showPanel('error');
}

// ── Rating slider ─────────────────────────────────────────────────────────────
ratingInput.addEventListener('input', () => {
  ratingDisplay.textContent = parseFloat(ratingInput.value).toFixed(1) + ' ★';
});

// ── Cuisine multi-select ──────────────────────────────────────────────────────
function openPanel() {
  panelOpen = true;
  msPanel.style.display = 'block';
  msTrigger.setAttribute('aria-expanded', 'true');
  msSearch.value = '';
  renderOptions(allCuisines);
  msSearch.focus();
}

function closePanel() {
  panelOpen = false;
  msPanel.style.display = 'none';
  msTrigger.setAttribute('aria-expanded', 'false');
}

// Toggle on trigger click
msTrigger.addEventListener('click', function (e) {
  e.stopPropagation();        // prevent document handler from firing on same event
  if (panelOpen) closePanel();
  else openPanel();
});

// Close when clicking outside
document.addEventListener('click', function (e) {
  if (panelOpen && !msWrapper.contains(e.target)) {
    closePanel();
  }
});

// Search filter
msSearch.addEventListener('input', function () {
  const q = msSearch.value.toLowerCase();
  const filtered = allCuisines.filter(c => c.toLowerCase().includes(q));
  renderOptions(filtered);
});

// Prevent clicks inside the panel from bubbling to document
msPanel.addEventListener('click', function (e) {
  e.stopPropagation();
});

function renderOptions(list) {
  if (list.length === 0) {
    msList.innerHTML = '<div class="ms-empty">No cuisines match</div>';
    return;
  }
  msList.innerHTML = list.map(c => {
    const sel = selectedCuisines.has(c);
    return `<label class="ms-option${sel ? ' selected' : ''}">
      <input type="checkbox" value="${escHtml(c)}"${sel ? ' checked' : ''} />
      ${escHtml(c)}
    </label>`;
  }).join('');

  msList.querySelectorAll('input[type="checkbox"]').forEach(function (cb) {
    cb.addEventListener('change', function () {
      if (cb.checked) selectedCuisines.add(cb.value);
      else selectedCuisines.delete(cb.value);
      updateChips();
      // Re-render to keep checked states in sync
      const q = msSearch.value.toLowerCase();
      renderOptions(allCuisines.filter(c => c.toLowerCase().includes(q)));
    });
  });
}

function updateChips() {
  if (selectedCuisines.size === 0) {
    msTriggerText.textContent = 'Any cuisine';
    msChips.innerHTML = '';
    return;
  }
  msTriggerText.textContent = selectedCuisines.size + ' selected';
  msChips.innerHTML = Array.from(selectedCuisines).map(c =>
    `<span class="ms-chip">${escHtml(c)}<button type="button" class="ms-chip-remove" data-val="${escHtml(c)}">×</button></span>`
  ).join('');
  msChips.querySelectorAll('.ms-chip-remove').forEach(function (btn) {
    btn.addEventListener('click', function () {
      selectedCuisines.delete(btn.dataset.val);
      updateChips();
      const q = msSearch.value.toLowerCase();
      renderOptions(allCuisines.filter(c => c.toLowerCase().includes(q)));
    });
  });
}

// ── Load dropdowns from API ───────────────────────────────────────────────────
async function initDropdowns() {
  // Load locations
  try {
    const res       = await fetch('/locations');
    const locations = await res.json();
    const sel = document.getElementById('location');
    sel.innerHTML = '<option value="" disabled selected>Select a location…</option>';
    locations.forEach(function (loc) {
      const opt = document.createElement('option');
      opt.value = loc;
      opt.textContent = loc;
      sel.appendChild(opt);
    });
  } catch (err) {
    const sel = document.getElementById('location');
    sel.innerHTML = '<option value="" disabled selected>Could not load locations</option>'
                  + '<option value="Bangalore">Bangalore</option>';
  }

  // Load cuisines
  try {
    const res      = await fetch('/cuisines');
    allCuisines    = await res.json();
    renderOptions(allCuisines);
  } catch (err) {
    msList.innerHTML = '<div class="ms-empty">Could not load cuisines</div>';
  }
}

// ── Form submit ───────────────────────────────────────────────────────────────
form.addEventListener('submit', async function (e) {
  e.preventDefault();
  closePanel();

  const location = document.getElementById('location').value.trim();
  if (!location) {
    showError('Location required', 'Please select a location from the dropdown.');
    return;
  }

  const budget     = form.querySelector('input[name="budget"]:checked');
  const minRating  = parseFloat(ratingInput.value) || null;
  const additional = document.getElementById('additional').value.trim() || null;
  const cuisine    = selectedCuisines.size > 0
    ? Array.from(selectedCuisines).join(', ')
    : null;

  const payload = {
    location,
    budget: budget ? budget.value : 'medium',
    cuisine,
    min_rating: minRating,
    additional_preferences: additional,
  };

  setLoading(true);
  showPanel('loading');

  try {
    const res  = await fetch('/recommend', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });
    const json = await res.json();

    if (!res.ok) {
      const detail = json.detail;
      const msg = Array.isArray(detail)
        ? detail.map(function (d) { return d.msg; }).join('; ')
        : String(detail || 'Unknown error.');
      showError('Request error', msg);
      return;
    }

    renderResults(json);
  } catch (err) {
    showError('Connection error', 'Could not reach the server. Is it running on port 8000?');
  } finally {
    setLoading(false);
  }
});

// ── Loading state ─────────────────────────────────────────────────────────────
function setLoading(on) {
  submitBtn.disabled        = on;
  btnText.textContent       = on ? 'Searching…' : 'Find Restaurants';
  btnSpinner.style.display  = on ? 'inline-block' : 'none';
}

// ── Render results ────────────────────────────────────────────────────────────
function renderResults(data) {
  if (data.status === 'error') {
    showError('No results', data.error_detail || 'The request could not be completed.');
    return;
  }
  if (data.status === 'no_results' || data.recommendations.length === 0) {
    showError(
      'No restaurants found',
      data.error_detail || 'Try a different location, lower the minimum rating, or widen the budget.'
    );
    return;
  }

  resultsMeta.innerHTML =
    `<span class="meta-chip success">✓ ${data.recommendations.length} recommendations</span>` +
    `<span class="meta-chip">📍 ${escHtml(data.city)}</span>` +
    `<span class="meta-chip">🔍 ${data.total_candidates_found.toLocaleString()} candidates screened</span>` +
    `<span class="meta-chip">⏱ ${data.latency_ms.toFixed(0)} ms</span>` +
    (data.fallback_used
      ? `<span class="meta-chip warn">⚠ AI unavailable — baseline ranking used</span>`
      : `<span class="meta-chip success">✨ AI ranked</span>`);

  let html = '';
  if (data.fallback_used && data.error_detail) {
    html += `<div class="fallback-banner"><span class="fallback-icon">⚠️</span>
      <span>Gemini was unavailable — showing baseline ranking. <em>${escHtml(data.error_detail)}</em></span>
    </div>`;
  }
  html += data.recommendations.map(renderCard).join('');
  resultsList.innerHTML = html;

  // Wire signal toggles
  resultsList.querySelectorAll('.sig-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const body = document.getElementById(btn.dataset.target);
      const open = body.style.display !== 'none';
      body.style.display = open ? 'none' : 'grid';
      btn.classList.toggle('open', !open);
    });
  });

  showPanel('results');
}

function renderCard(rec) {
  const rankClass = rec.rank <= 3 ? 'rank-' + rec.rank : 'rank-other';
  const cuisineTags = rec.cuisine.split(',')
    .map(function (c) { return `<span class="cuisine-tag">${escHtml(c.trim())}</span>`; })
    .join('');

  const confClass = 'confidence-' + rec.confidence;
  const confLabel = rec.confidence.charAt(0).toUpperCase() + rec.confidence.slice(1);

  const tradeoffHtml = rec.tradeoffs
    ? `<div class="card-tradeoffs"><span class="tradeoffs-icon">⚖️</span><span>${escHtml(rec.tradeoffs)}</span></div>`
    : '';

  const signals   = rec.match_signals || {};
  const signalsId = 'sig-' + rec.restaurant_id;
  const sigRows   = Object.entries(signals).map(function (entry) {
    const key = entry[0], val = entry[1];
    const label = key.replace(/_/g, ' ');
    if (typeof val === 'boolean') {
      return `<div class="signal-item"><span class="signal-name">${escHtml(label)}</span>
        <span class="signal-value">${val ? '✓ Yes' : '✗ No'}</span></div>`;
    }
    const pct = Math.min(1, Math.max(0, parseFloat(val) || 0));
    return `<div class="signal-item"><span class="signal-name">${escHtml(label)}</span>
      <span class="signal-value" style="display:flex;align-items:center;gap:4px">
        ${(pct * 100).toFixed(0)}%
        <span class="signal-bar-wrap"><span class="signal-bar" style="width:${pct * 100}%"></span></span>
      </span></div>`;
  }).join('');

  return `<div class="restaurant-card">
    <div class="card-header">
      <div class="rank-badge ${rankClass}">#${rec.rank}</div>
      <div class="card-title-row">
        <div class="card-name">${escHtml(rec.restaurant_name)}</div>
        <div class="card-cuisine-tags">${cuisineTags}</div>
      </div>
    </div>
    <div class="card-stats">
      <div class="stat"><span class="stat-icon">⭐</span><span class="stat-value">${rec.rating.toFixed(1)}</span><span class="stat-label">/5</span></div>
      <div class="stat"><span class="stat-icon">₹</span><span class="stat-value">${rec.estimated_cost.toLocaleString()}</span><span class="stat-label">for two</span></div>
      <div class="stat"><span class="stat-icon">👥</span><span class="stat-value">${rec.votes.toLocaleString()}</span><span class="stat-label">votes</span></div>
      <span class="confidence-badge ${confClass}">${confLabel} confidence</span>
    </div>
    <div class="card-explanation">${escHtml(rec.ai_explanation)}</div>
    ${tradeoffHtml}
    ${sigRows ? `
      <button class="match-signals-toggle sig-toggle" data-target="${signalsId}">
        <span class="toggle-arrow">▶</span> Match signals
      </button>
      <div class="match-signals-body" id="${signalsId}" style="display:none">${sigRows}</div>` : ''}
  </div>`;
}

// ── Utility ───────────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Boot ──────────────────────────────────────────────────────────────────────
showPanel('empty');
initDropdowns();
