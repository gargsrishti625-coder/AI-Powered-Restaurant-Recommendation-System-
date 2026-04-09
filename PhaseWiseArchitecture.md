# Detailed Phase-Wise Architecture  
AI-Powered Restaurant Recommendation System (Zomato Use Case)

This document expands the project into detailed, executable phases with architecture, components, interfaces, data contracts, and deliverables.

---

## 1) Phase 1: Data Foundation and Ingestion

### Objective
Build a trusted, queryable restaurant data layer from the Hugging Face Zomato dataset.

### Architecture
- **Data Source Layer**
  - Hugging Face dataset: `ManikaSaini/zomato-restaurant-recommendation`
- **Ingestion Layer**
  - Batch loader script/notebook to fetch raw data
- **Processing Layer**
  - Cleaning + normalization pipeline
- **Storage Layer**
  - Relational DB for serving recommendations
- **Metadata Layer**
  - Data quality reports, schema version, ingestion timestamp

### Core Components
- `dataset_loader.py`
  - Pulls data from Hugging Face and stores raw snapshot
- `preprocess_pipeline.py`
  - Handles missing values, type conversions, feature extraction
- `schema.py`
  - Canonical schema and validation rules
- `db_writer.py`
  - Writes curated records into DB tables

### Canonical Schema (restaurants table)
- `restaurant_id` (string/int, primary key)
- `name` (string)
- `city` (string)
- `locality` (string)
- `cuisines` (array<string> or comma-separated string)
- `avg_cost_for_two` (float/int)
- `rating` (float)
- `votes` (int)
- `currency` (string)
- `is_table_booking` (bool, optional)
- `is_online_delivery` (bool, optional)
- `tags` (array<string>, optional)
- `last_updated_at` (timestamp)

### Processing Rules
- Normalize city/locality casing and whitespace
- Convert cost fields to numeric
- Normalize rating to float in consistent range
- Split cuisines into clean tokens
- Drop duplicate restaurants by stable keys
- Mark unverifiable values with null + quality flags

### Output
- Curated `restaurants` table
- Data quality report (null ratios, unique counts, range checks)
- Re-runnable ingestion command

### Exit Criteria
- >95% rows pass schema validation
- All mandatory fields populated: name, city, cuisines, cost, rating
- Query latency for filtered lookup acceptable on sample tests

---

## 2) Phase 2: User Preference Capture and Normalization

### Objective
Collect user preferences and convert them into machine-usable filters/signals.

### Architecture
- **Presentation Layer**
  - Input form (web UI)
- **Validation Layer**
  - Required fields, type checks, allowed enums
- **Normalization Layer**
  - Maps raw text to standardized preference object
- **Session Layer (optional)**
  - Persist recent user preferences for retries/regeneration

### Input Contract (raw)
- `location` (string)
- `budget` (enum or string: low/medium/high)
- `cuisine` (string or list)
- `min_rating` (float)
- `additional_preferences` (free text)

### Normalized Contract (`UserPreference`)
- `city`: string
- `budget_range`: `{min_cost: number, max_cost: number}`
- `cuisine_preferences`: string[]
- `min_rating`: float
- `keywords`: string[] (from additional preferences)
- `sort_bias`: string[] (optional, e.g., "value", "quality")

### Rules
- Budget mapping:
  - `low`: 0-700
  - `medium`: 700-2000
  - `high`: 2000+
  - Values are configurable in settings.
- Cuisine synonym mapping:
  - Example: `north indian` -> `indian`
- Location normalization:
  - Trim, case normalize, city alias handling
- Additional preference extraction:
  - Keyword parser for tags like `family-friendly`, `quick service`

### Output
- Strictly validated `UserPreference` object for downstream layers

### Exit Criteria
- Invalid requests rejected with actionable errors
- >90% common input variants normalized correctly

---

## 3) Phase 3: Candidate Retrieval and Baseline Ranking

### Objective
Use deterministic logic to retrieve top candidate restaurants before LLM reasoning.

### Architecture
- **Filter Engine**
  - SQL/ORM query layer for hard constraints
- **Scoring Engine**
  - Weighted score to rank candidates
- **Candidate Packaging Layer**
  - Produces a compact structured list for LLM context

### Retrieval Steps
1. Filter by city/location
2. Filter by budget range
3. Filter by min rating
4. Soft match cuisines and preferences
5. Score and rank top `N` candidates (e.g., 20)

### Baseline Scoring (example)
- `score = 0.4 * rating_norm + 0.25 * cuisine_match + 0.2 * budget_fit + 0.15 * popularity_norm`
- `popularity_norm` from votes/reviews
- Apply slight penalty for sparse metadata

### Candidate Object
- `restaurant_id`
- `name`
- `city`
- `cuisines`
- `rating`
- `avg_cost_for_two`
- `votes`
- `match_features` (budget_fit, cuisine_match, rating_pass)
- `baseline_score`

### Why This Layer Is Critical
- Reduces LLM token usage and cost
- Improves grounding and factuality
- Provides fallback recommendations if LLM fails

### Exit Criteria
- Deterministic retrieval returns relevant candidates for test personas
- Candidate set size remains bounded and stable

---

## 4) Phase 4: LLM Orchestration and Explainable Ranking

### Objective
Rank shortlisted restaurants and generate personalized explanations.

### Architecture
- **Prompt Builder**
  - Converts user profile + candidates into robust prompt template
- **LLM Gateway**
  - Uses Gemini LLM for ranking and explanation generation
  - Handles model calls, retries, timeouts, and safety checks
  - Loads Gemini API key from `.env` (for example, `GEMINI_API_KEY`)
- **Output Validator**
  - Enforces JSON schema and candidate-grounded responses
- **Post-Processor**
  - Sanitizes language, trims verbosity, standardizes explanation length

### Prompt Structure
- **System role**
  - "You are a restaurant recommendation expert. Use only provided candidates."
- **User profile block**
  - Normalized preferences
- **Candidate block**
  - Structured list (JSON-like)
- **Task block**
  - Rank top K, explain "why fit", avoid hallucinated attributes
- **Output schema block**
  - Fixed JSON keys for deterministic parsing

### Recommended Output Contract
- `recommendations`: array of
  - `restaurant_id`
  - `rank`
  - `fit_reason` (2-3 concise lines)
  - `tradeoffs` (optional)
  - `confidence` (low/medium/high)

### Reliability Controls
- Retry policy for transient API failures
- Timeout and fallback to baseline ranking
- Strict schema validation before API response
- Reject restaurants not present in candidate set

### Exit Criteria
- 100% parsed responses on test prompts
- Explanations are candidate-grounded and user-specific

---

## 5) Phase 5: Recommendation Service API Layer

### Objective
Expose a production-usable recommendation endpoint and orchestration flow.

### Architecture
- **API Gateway / Backend App**
  - `POST /recommend`
- **Recommendation Orchestrator**
  - Calls normalization -> retrieval -> LLM -> formatting
- **Error Handler**
  - Graceful fallback path
- **Telemetry**
  - Request IDs, timing, token usage, error logging

### Endpoint Design
- **Request**
  - Raw user inputs from frontend
- **Response**
  - Top recommendations with AI explanation and key metadata

### Response Example Fields
- `request_id`
- `status`
- `recommendations`:
  - `restaurant_name`
  - `cuisine`
  - `rating`
  - `estimated_cost`
  - `ai_explanation`
  - `match_signals`
- `fallback_used` (bool)

### Non-Functional Requirements
- P95 API latency target (for example, <2.5s with caching)
- Idempotent behavior for duplicate client retries
- Basic rate limiting for abuse control

### Exit Criteria
- Stable API responses under expected load
- Consistent error format and fallback behavior

---

## 6) Phase 6: Frontend Experience and Interaction Design

> **Status: IMPLEMENTED (Next.js UI)** — Rebuilt as a Next.js 16 app in `frontend/`. FastAPI backend unchanged.

### Objective
Deliver clear recommendation UX with transparency and quick refinements, inspired by Zomato AI's curated journey design.

### Implementation

#### Frontend Stack (Next.js)
- **Framework**: Next.js 16 (App Router, Turbopack) + TypeScript + Tailwind CSS
- **Directory**: `frontend/`
- **Dev server**: `http://localhost:3000`
- **API proxy**: Next.js rewrites `/api/*` → `http://localhost:8000/*` (no CORS issue)
- **CORS**: FastAPI allows `http://localhost:3000` via `CORSMiddleware`

#### File Structure
```
frontend/
├── app/
│   ├── layout.tsx         — root layout, metadata
│   ├── page.tsx           — main page (client component, state management)
│   └── globals.css        — Tailwind + skeleton animation
├── components/
│   ├── Header.tsx         — sticky nav bar (Zomato AI branding)
│   ├── Sidebar.tsx        — Smart Filters panel (right column)
│   ├── ResultsPanel.tsx   — AI Journey header + card grid + skeleton loader
│   └── RestaurantCard.tsx — individual card with cuisine gradient, AI insight
├── lib/
│   ├── api.ts             — fetchLocations, fetchCuisines, fetchRecommendations
│   └── types.ts           — TypeScript interfaces (RecommendRequest/Response)
└── next.config.ts         — rewrites proxy config
```

#### API endpoints used by frontend
- `GET /locations` — 30 Bangalore localities (no "Bangalore" catch-all)
- `GET /cuisines` — 104 unique cuisines (deduplicated, e.g. Afghani consolidated)
- `POST /recommend` — full recommendation pipeline

### Architecture
- **Input Experience (Sidebar)**
  - Location: native `<select>` populated from `/api/locations`
  - Budget: three-button visual selector (₹ / ₹₹ / ₹₹₹)
  - Cuisine: searchable multi-select dropdown with chips, optional
  - Rating: range slider
  - Additional Preferences: textarea, optional
  - Active Criteria: chips showing current filters with × to remove
- **Results Experience**
  - "AI Curated Journey" header with city, cuisine, budget summary
  - Refresh Suggestions button (re-runs last query)
  - Top result: featured wide card
  - Remaining results: 2-column responsive grid
  - Each card: cuisine-based gradient image, rating badge, rank badge, AI Insight quote
  - Skeleton shimmer loading state
- **State Layer**
  - Empty → Loading (skeleton) → Results / Error transitions
  - Clear filter chips trigger a re-query
  - Fallback badge shown when LLM is unavailable

### UX Requirements
- Show loading skeleton while LLM runs ✅
- Show deterministic fallback if AI output unavailable ✅
- Keep explanations concise and scan-friendly ✅
- Location and cuisine use dropdowns populated from live API ✅
- Cuisine and additional preferences are optional ✅
- Design inspired by Zomato AI (curated journey, AI Insight card, active filter chips) ✅

### To Run
```bash
# Terminal 1 — Backend (FastAPI)
cd "AI Restaurant Recommender"
.venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Frontend (Next.js)
cd "AI Restaurant Recommender/frontend"
npm run dev
# Open: http://localhost:3000
```

> The old vanilla HTML/CSS/JS UI is still available at `http://localhost:8000` (served by FastAPI).

### Exit Criteria
- User can complete end-to-end journey in under 1 minute ✅
- Recommendation rationale is understandable without technical context ✅

---

## 7) Phase 7: Quality Evaluation, Monitoring, and Continuous Improvement

### Objective
Measure recommendation quality and improve models/rules iteratively.

### Architecture
- **Evaluation Layer**
  - Offline benchmark suite with labeled scenarios
- **Feedback Layer**
  - User feedback capture (like/dislike/save/click)
- **Analytics Layer**
  - Metrics dashboard for quality, latency, usage, and failures
- **Improvement Loop**
  - Tune filters, weights, prompts, and model choice

### Key Metrics
- Relevance metrics:
  - Precision@K for cuisine/budget/location fit
- Behavior metrics:
  - CTR, save rate, repeat usage
- System metrics:
  - Latency, failure rate, token cost per request

### Improvement Levers
- Adjust baseline scoring weights
- Prompt iteration with A/B testing
- Add reranking heuristics for special preferences
- Add city-specific calibration

### Exit Criteria
- Measurable quality uplift across release cycles
- Observability available for operational decisions

---

## 8) Cross-Cutting Architecture (Applies to All Phases)

### Security and Privacy
- Validate and sanitize all user inputs
- Avoid storing personally identifiable data unless required
- Keep API keys in environment variables or secret manager

### Configuration Management
- Central config for:
  - budget thresholds
  - ranking weights
  - top N candidates
  - model/provider selection

### Caching Strategy
- Cache repeated candidate retrievals by normalized query signature
- Cache LLM recommendations with short TTL for common requests

### Testing Strategy
- Unit tests:
  - normalizers, filters, scoring, schema validation
- Integration tests:
  - recommendation flow with mocked LLM
- End-to-end tests:
  - UI form -> API -> rendered recommendations

### Deployment Topology (MVP)
- Single backend service + DB + frontend app
- Scheduled batch job for dataset refresh
- Logging/monitoring enabled from day one

---

## 9) Suggested Repository Structure

- `data/`
  - `raw/`, `processed/`, `quality_reports/`
- `src/`
  - `api/` (routes, request/response models)
  - `core/` (config, logging, constants)
  - `ingestion/` (load + preprocess)
  - `retrieval/` (filters + baseline scoring)
  - `llm/` (prompt templates, model client, validators)
  - `orchestration/` (end-to-end recommendation flow)
  - `ui/` (if monorepo; else separate frontend repo)
- `tests/`
  - `unit/`, `integration/`, `e2e/`
- `docs/`
  - architecture, API spec, prompt versions

---

## 10) Deployment

### Overview

| Layer    | Platform   | Technology          |
|----------|------------|---------------------|
| Backend  | Streamlit  | Python / FastAPI    |
| Frontend | Vercel     | Next.js (App Router)|

---

### Backend: Streamlit Cloud

The Python backend (FastAPI + recommendation pipeline) is deployed on **Streamlit Community Cloud** or wrapped as a Streamlit app.

#### Deployment Steps
1. Push the repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect the repository.
3. Set the entry point to the Streamlit app file (e.g., `app.py` or `src/api/main.py`).
4. Add secrets in the Streamlit Cloud dashboard under **Settings → Secrets**:
   - `GEMINI_API_KEY`
   - Any other keys from `.env`
5. Streamlit auto-deploys on every push to the configured branch.

#### Environment Variables (Streamlit Secrets)
```toml
# .streamlit/secrets.toml (local dev only — never commit)
GEMINI_API_KEY = "your-key-here"
HF_DATASET_NAME = "ManikaSaini/zomato-restaurant-recommendation"
PHASE3_TOP_N_CANDIDATES = "20"
```

#### CORS Configuration
The FastAPI backend must allow the Vercel frontend domain:
```python
# src/api/main.py
origins = [
    "http://localhost:3000",
    "https://<your-project>.vercel.app",  # add after Vercel deploy
]
```

---

### Frontend: Vercel

The Next.js frontend (`frontend/`) is deployed on **Vercel**.

#### Deployment Steps
1. Push the repo to GitHub.
2. Import the project in the [Vercel dashboard](https://vercel.com/new), setting the **Root Directory** to `frontend/`.
3. Add environment variables in the Vercel dashboard under **Settings → Environment Variables**:
   - `NEXT_PUBLIC_API_URL` — the public URL of the deployed Streamlit/FastAPI backend (e.g., `https://<your-app>.streamlit.app`)
4. Vercel auto-deploys on every push to the configured branch.

#### next.config.ts — API Proxy for Production
Update the rewrites to point to the deployed backend URL:
```ts
// frontend/next.config.ts
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: process.env.NEXT_PUBLIC_API_URL
          ? `${process.env.NEXT_PUBLIC_API_URL}/:path*`
          : "http://localhost:8000/:path*",
      },
    ];
  },
};
export default nextConfig;
```

---

### Data Flow (Production)

```
User (Browser)
      │
      ▼
Vercel (Next.js frontend)
      │  POST /api/recommend
      ▼
Streamlit Cloud (FastAPI backend)
      │
      ├── SQLite / in-memory DB  (restaurant data)
      └── Gemini API             (LLM ranking)
```

---

### Deployment Checklist

- [ ] `.env` values added to Streamlit Secrets and Vercel Environment Variables
- [ ] Vercel `NEXT_PUBLIC_API_URL` set to the live Streamlit backend URL
- [ ] FastAPI `CORSMiddleware` updated to allow the Vercel domain
- [ ] `frontend/next.config.ts` rewrites use `NEXT_PUBLIC_API_URL` in production
- [ ] `.env` and `.streamlit/secrets.toml` are in `.gitignore`
- [ ] Gemini API key rotated if previously exposed

---

---

## 11) Environment Variables (.env)

Use a `.env` file in the project root to keep configuration and secrets out of code.

### Phase 1 (Data Foundation and Ingestion)
- `HF_DATASET_NAME` (default: `ManikaSaini/zomato-restaurant-recommendation`)
- `HF_DATASET_SPLIT` (default: `train`)
- `PHASE1_SOURCE_PRIORITY` (`huggingface` or `local`)
- `PHASE1_LOCAL_CSV_PATH` (default: `data/zomato.csv`)
- `PHASE1_TABLE_NAME` (default: `restaurants`)
- `WORKSPACE_ROOT` (optional override for local paths)

### Phase 2 (User Preference Capture and Normalization)
- No mandatory secret keys.
- Optional future config keys can be added for budget thresholds and synonym maps.

### Phase 3 (Candidate Retrieval and Baseline Ranking)
- `PHASE3_TOP_N_CANDIDATES` (default: `20`)
- Optional future keys for scoring weights:
  - `PHASE3_WEIGHT_RATING`
  - `PHASE3_WEIGHT_CUISINE`
  - `PHASE3_WEIGHT_BUDGET`
  - `PHASE3_WEIGHT_POPULARITY`

### Phase 4 (LLM Orchestration and Explainable Ranking)
- `GEMINI_API_KEY` (required for Gemini LLM calls)
- Optional model/runtime keys:
  - `GEMINI_MODEL` (for example, `gemini-1.5-pro` / `gemini-1.5-flash`)
  - `LLM_TIMEOUT_SECONDS`
  - `LLM_MAX_RETRIES`

### Security Notes
- Never hardcode secrets in source files.
- Add `.env` to `.gitignore`.
- Rotate keys immediately if exposed.

This phased architecture is designed to move from dependable data foundations to explainable AI recommendations with production readiness.
