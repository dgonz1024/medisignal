from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])


HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MediSignal</title>
  <style>
    :root {
      --bg: #f4efe7;
      --panel: rgba(255, 252, 247, 0.86);
      --panel-strong: #fffaf3;
      --ink: #1f2a2c;
      --muted: #667377;
      --line: rgba(42, 58, 61, 0.12);
      --accent: #1b7f6b;
      --accent-soft: #dff3ed;
      --accent-warm: #d88a37;
      --shadow: 0 24px 80px rgba(31, 42, 44, 0.10);
      --radius: 22px;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(216, 138, 55, 0.14), transparent 30%),
        radial-gradient(circle at top right, rgba(27, 127, 107, 0.16), transparent 28%),
        linear-gradient(180deg, #f6f1ea 0%, #f1ebe2 100%);
      min-height: 100vh;
    }

    .shell {
      width: min(1280px, calc(100% - 32px));
      margin: 24px auto 40px;
    }

    .page-nav {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      margin-bottom: 14px;
      padding: 10px 16px;
      background: rgba(255, 250, 243, 0.7);
      border: 1px solid rgba(42, 58, 61, 0.08);
      border-radius: 999px;
      backdrop-filter: blur(10px);
      box-shadow: 0 12px 30px rgba(31, 42, 44, 0.06);
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .page-nav strong {
      font-size: 0.95rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--ink);
    }

    .page-nav-links {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .page-nav a {
      text-decoration: none;
      color: var(--muted);
      padding: 8px 12px;
      border-radius: 999px;
      transition: background 120ms ease, color 120ms ease;
    }

    .page-nav a:hover {
      background: rgba(27, 127, 107, 0.1);
      color: var(--accent);
    }

    .hero {
      background: linear-gradient(135deg, rgba(255, 250, 243, 0.94), rgba(245, 255, 251, 0.92));
      border: 1px solid rgba(42, 58, 61, 0.08);
      border-radius: 28px;
      box-shadow: var(--shadow);
      padding: 28px;
      position: relative;
      overflow: hidden;
    }

    .hero::after {
      content: "";
      position: absolute;
      inset: auto -10% -60% auto;
      width: 280px;
      height: 280px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(27, 127, 107, 0.18), transparent 65%);
      pointer-events: none;
    }

    .hero-layout {
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.85fr);
      gap: 20px;
      align-items: start;
    }

    .eyebrow {
      font-size: 12px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 10px;
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    h1 {
      font-size: clamp(2.2rem, 4vw, 4.4rem);
      line-height: 0.95;
      margin: 0 0 14px;
      max-width: 8ch;
      font-weight: 600;
    }

    .hero p {
      margin: 0;
      max-width: 56rem;
      color: var(--muted);
      font-size: 1.05rem;
      line-height: 1.6;
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .hero-rail {
      display: grid;
      gap: 12px;
    }

    .rail-card {
      padding: 18px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.66);
      border: 1px solid rgba(42, 58, 61, 0.08);
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .rail-card h2 {
      margin: 0 0 10px;
      font-size: 1rem;
      font-family: Georgia, "Times New Roman", serif;
    }

    .rail-list {
      display: grid;
      gap: 10px;
      color: var(--muted);
      font-size: 0.94rem;
      line-height: 1.5;
    }

    .rail-actions {
      display: grid;
      gap: 10px;
    }

    .action-chip {
      appearance: none;
      border: 1px solid rgba(27, 127, 107, 0.12);
      background: var(--panel-strong);
      color: var(--ink);
      border-radius: 16px;
      padding: 12px 14px;
      text-align: left;
      cursor: pointer;
      transition: transform 120ms ease, border-color 120ms ease, background 120ms ease;
    }

    .action-chip:hover {
      transform: translateY(-1px);
      border-color: rgba(27, 127, 107, 0.28);
      background: rgba(223, 243, 237, 0.75);
    }

    .action-chip strong {
      display: block;
      margin-bottom: 4px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 1rem;
    }

    .action-chip span {
      color: var(--muted);
      font-size: 0.9rem;
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 22px;
    }

    .stat-card,
    .panel,
    .detail-card {
      background: var(--panel);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(42, 58, 61, 0.08);
      box-shadow: var(--shadow);
      border-radius: var(--radius);
    }

    .stat-card {
      padding: 18px 20px;
    }

    .stat-label {
      font-size: 12px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--muted);
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .stat-value {
      font-size: 2rem;
      margin-top: 10px;
    }

    .grid {
      display: grid;
      grid-template-columns: 1.6fr 0.9fr;
      gap: 18px;
      margin-top: 18px;
      align-items: start;
    }

    .section-shell {
      margin-top: 18px;
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 12px;
      margin: 8px 0 12px;
    }

    .section-header h2 {
      margin: 0;
      font-size: 1.5rem;
    }

    .section-header p {
      margin: 6px 0 0;
      color: var(--muted);
      font-family: "Helvetica Neue", Arial, sans-serif;
      line-height: 1.5;
      max-width: 48rem;
    }

    .section-kicker {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--accent);
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .panel {
      padding: 20px;
    }

    .panel h2 {
      margin: 0 0 14px;
      font-size: 1.4rem;
    }

    .controls {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }

    .field {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .field label {
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .field input,
    .field select,
    .field button {
      appearance: none;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: var(--panel-strong);
      color: var(--ink);
      padding: 12px 14px;
      font-size: 0.96rem;
      min-height: 46px;
    }

    .field button {
      background: linear-gradient(135deg, var(--accent), #0f6554);
      color: white;
      font-weight: 600;
      cursor: pointer;
      transition: transform 120ms ease, box-shadow 120ms ease;
      box-shadow: 0 16px 32px rgba(27, 127, 107, 0.22);
    }

    .field button:hover {
      transform: translateY(-1px);
    }

    .toolbar {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: start;
      gap: 12px;
      margin-bottom: 14px;
      font-family: "Helvetica Neue", Arial, sans-serif;
      color: var(--muted);
    }

    #results-summary {
      line-height: 1.5;
      min-width: 0;
    }

    .pager {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .pager .hidden {
      display: none;
    }

    .page-jump {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .page-jump label {
      color: var(--muted);
      font-size: 0.9rem;
    }

    .page-jump input {
      width: 64px;
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: var(--panel-strong);
      padding: 8px 10px;
      color: var(--ink);
      font-size: 0.95rem;
    }

    .page-jump button {
      min-height: 38px;
      border: 0;
      border-radius: 12px;
      background: rgba(27, 127, 107, 0.12);
      color: var(--accent);
      padding: 8px 12px;
      cursor: pointer;
      font-weight: 600;
    }

    .context-bar {
      display: none;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 14px;
      padding: 12px 14px;
      border-radius: 16px;
      background: rgba(223, 243, 237, 0.6);
      border: 1px solid rgba(27, 127, 107, 0.12);
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .context-bar.active {
      display: flex;
    }

    .context-copy {
      color: var(--ink);
      line-height: 1.5;
    }

    .context-clear {
      appearance: none;
      border: 0;
      background: transparent;
      color: var(--accent);
      cursor: pointer;
      font-weight: 600;
    }

    .preset-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 0 0 18px;
    }

    .preset-button {
      appearance: none;
      border: 1px solid rgba(42, 58, 61, 0.1);
      background: rgba(255, 255, 255, 0.7);
      color: var(--ink);
      border-radius: 999px;
      padding: 10px 14px;
      font-family: "Helvetica Neue", Arial, sans-serif;
      cursor: pointer;
      transition: background 120ms ease, border-color 120ms ease;
    }

    .preset-button:hover {
      background: rgba(223, 243, 237, 0.7);
      border-color: rgba(27, 127, 107, 0.2);
    }

    .table {
      display: grid;
      gap: 10px;
    }

    .trial-row {
      display: grid;
      grid-template-columns: 1.8fr 0.6fr 0.8fr 0.8fr;
      gap: 12px;
      align-items: center;
      padding: 16px;
      border-radius: 18px;
      border: 1px solid rgba(42, 58, 61, 0.08);
      background: rgba(255, 255, 255, 0.5);
      cursor: pointer;
      transition: transform 120ms ease, background 120ms ease, border-color 120ms ease;
    }

    .trial-row:hover {
      transform: translateY(-1px);
      background: rgba(255, 255, 255, 0.82);
      border-color: rgba(27, 127, 107, 0.2);
    }

    .trial-row.active {
      border-color: rgba(27, 127, 107, 0.55);
      background: rgba(184, 229, 216, 0.78);
      box-shadow: inset 0 0 0 1px rgba(27, 127, 107, 0.14);
    }

    .trial-title {
      font-weight: 600;
      margin-bottom: 6px;
    }

    .trial-meta,
    .pill,
    .mini-list,
    .empty,
    .detail-copy {
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .trial-meta {
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.5;
    }

    .metric {
      text-align: right;
    }

    .metric strong {
      display: block;
      font-size: 1.1rem;
    }

    .metric span {
      color: var(--muted);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .detail-card {
      padding: 20px;
      position: sticky;
      top: 20px;
      max-height: calc(100vh - 40px);
      overflow-y: auto;
      scrollbar-width: thin;
      scrollbar-color: rgba(27, 127, 107, 0.35) rgba(42, 58, 61, 0.08);
    }

    .detail-card::-webkit-scrollbar {
      width: 10px;
    }

    .detail-card::-webkit-scrollbar-track {
      background: rgba(42, 58, 61, 0.06);
      border-radius: 999px;
    }

    .detail-card::-webkit-scrollbar-thumb {
      background: rgba(27, 127, 107, 0.35);
      border-radius: 999px;
    }

    .detail-card h3 {
      font-size: 1.4rem;
      margin: 0 0 10px;
    }

    .detail-copy {
      color: var(--muted);
      line-height: 1.6;
    }

    .detail-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin: 18px 0;
    }

    .mini-card {
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid rgba(42, 58, 61, 0.07);
      border-radius: 16px;
      padding: 12px;
    }

    .mini-card span {
      display: block;
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 8px;
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .mini-card strong {
      display: block;
      overflow-wrap: normal;
      word-break: normal;
      line-height: 1.3;
    }

    .pill-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 14px 0 18px;
    }

    .pill {
      background: var(--accent-soft);
      color: #0c5d4d;
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 0.88rem;
    }

    .section-title {
      margin: 18px 0 10px;
      font-size: 1rem;
    }

    .mini-list {
      display: grid;
      gap: 10px;
      color: var(--muted);
      font-size: 0.95rem;
    }

    .mini-list strong {
      color: var(--ink);
    }

    .leaders {
      display: grid;
      gap: 12px;
    }

    .analytics-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 18px;
      margin-top: 18px;
    }

    .research-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
      margin-top: 18px;
    }

    .leader {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 14px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.58);
      border: 1px solid rgba(42, 58, 61, 0.07);
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .leader.clickable {
      cursor: pointer;
      transition: transform 120ms ease, border-color 120ms ease, background 120ms ease;
    }

    .leader.clickable:hover {
      transform: translateY(-1px);
      border-color: rgba(27, 127, 107, 0.2);
      background: rgba(223, 243, 237, 0.58);
    }

    .leader strong {
      display: block;
      margin-bottom: 4px;
      color: var(--ink);
      font-family: Georgia, "Times New Roman", serif;
      font-size: 1rem;
    }

    .leader span {
      color: var(--muted);
      font-size: 0.9rem;
    }

    .empty {
      padding: 18px;
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.58);
      border: 1px dashed rgba(42, 58, 61, 0.16);
      color: var(--muted);
    }

    .status {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border-radius: 999px;
      padding: 8px 12px;
      background: rgba(216, 138, 55, 0.12);
      color: #8a4f13;
      font-family: "Helvetica Neue", Arial, sans-serif;
      font-size: 0.88rem;
    }

    .status::before {
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent-warm);
    }

    @media (max-width: 1080px) {
      .hero-layout,
      .stats-grid,
      .controls,
      .grid,
      .analytics-grid,
      .research-grid {
        grid-template-columns: 1fr 1fr;
      }

      .grid {
        grid-template-columns: 1fr;
      }

      .detail-card {
        position: static;
      }
    }

    @media (max-width: 720px) {
      .shell {
        width: min(100% - 20px, 100%);
        margin-top: 10px;
      }

      .page-nav {
        border-radius: 24px;
        align-items: start;
        flex-direction: column;
      }

      .hero,
      .panel,
      .detail-card {
        padding: 16px;
      }

      .stats-grid,
      .controls,
      .detail-grid,
      .analytics-grid,
      .research-grid {
        grid-template-columns: 1fr;
      }

      .trial-row {
        grid-template-columns: 1fr;
      }

      .metric {
        text-align: left;
      }

      .toolbar {
        grid-template-columns: 1fr;
      }

      .pager {
        justify-content: flex-start;
      }
    }
  </style>
</head>
  <body>
  <div class="shell">
    <nav class="page-nav">
      <strong>MediSignal</strong>
      <div class="page-nav-links">
        <a href="#overview">Overview</a>
        <a href="#explorer">Explorer</a>
        <a href="#patterns">Pattern Watch</a>
        <a href="#briefs">Research Briefs</a>
      </div>
    </nav>

    <section class="hero" id="overview">
      <div class="hero-layout">
        <div>
          <div class="eyebrow">Clinical Trial Data Platform</div>
          <h1>MediSignal Console</h1>
          <p>
            Browse cleaned ClinicalTrials.gov records, inspect trial detail, and explore research patterns from the local
            MediSignal pipeline without reading raw JSON by hand.
          </p>
        </div>
        <div class="hero-rail">
          <div class="rail-card">
            <h2>Start Here</h2>
            <div class="rail-list">
              <div>1. Use a quick view or filters to narrow the trial list.</div>
              <div>2. Click any trial to inspect the structured study detail.</div>
              <div>3. Use the research briefs to understand sponsor or condition patterns.</div>
            </div>
          </div>
          <div class="rail-card">
            <h2>Quick Views</h2>
            <div class="rail-actions">
              <button class="action-chip" data-preset="recruiting">
                <strong>Recruiting Trials</strong>
                <span>Focus on currently open studies.</span>
              </button>
              <button class="action-chip" data-preset="industry">
                <strong>Industry Sponsored</strong>
                <span>See commercially sponsored activity first.</span>
              </button>
              <button class="action-chip" data-preset="largest">
                <strong>Largest Studies</strong>
                <span>Sort by enrollment to spot big operational programs.</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Trials Indexed</div>
          <div class="stat-value" id="stat-total">--</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Top Condition</div>
          <div class="stat-value" id="stat-condition">--</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Top Sponsor</div>
          <div class="stat-value" id="stat-sponsor">--</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">API Status</div>
          <div class="stat-value" id="stat-health">--</div>
        </div>
      </div>
    </section>

    <section class="section-shell" id="explorer">
      <div class="section-header">
        <div>
          <div class="section-kicker">Explore Records</div>
          <h2>Trial Explorer</h2>
          <p>Start broad, then narrow down. The left side helps you find trials, and the right side turns a selected study into a cleaner summary.</p>
        </div>
      </div>
    </section>

    <section class="grid">
      <div class="panel">
        <div class="controls">
          <div class="field">
            <label for="status">Status</label>
            <select id="status">
              <option value="">Any</option>
              <option value="RECRUITING">Recruiting</option>
              <option value="COMPLETED">Completed</option>
              <option value="ACTIVE_NOT_RECRUITING">Active, Not Recruiting</option>
              <option value="NOT_YET_RECRUITING">Not Yet Recruiting</option>
              <option value="TERMINATED">Terminated</option>
            </select>
          </div>
          <div class="field">
            <label for="sponsor_type">Sponsor Type</label>
            <select id="sponsor_type">
              <option value="">Any</option>
              <option value="Industry">Industry</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div class="field">
            <label for="country">Country</label>
            <input id="country" list="country-suggestions" placeholder="United States" autocomplete="off" />
          </div>
          <div class="field">
            <label for="condition">Condition</label>
            <input id="condition" list="condition-suggestions" placeholder="Delirium" autocomplete="off" />
          </div>
          <div class="field">
            <label for="sponsor">Sponsor</label>
            <input id="sponsor" list="sponsor-suggestions" placeholder="GlaxoSmithKline" autocomplete="off" />
          </div>
          <div class="field">
            <label for="phase">Phase</label>
            <input id="phase" list="phase-suggestions" placeholder="PHASE2 or Unspecified" autocomplete="off" />
          </div>
          <div class="field">
            <label for="min_enrollment">Min Enrollment</label>
            <input id="min_enrollment" type="number" min="0" placeholder="100" />
          </div>
          <div class="field">
            <label for="sort_by">Sort By</label>
            <select id="sort_by">
              <option value="last_update_posted">Last Update</option>
              <option value="enrollment_count">Enrollment</option>
              <option value="location_count">Locations</option>
              <option value="condition_count">Conditions</option>
              <option value="brief_title">Title</option>
              <option value="sponsor_name">Sponsor</option>
            </select>
          </div>
          <div class="field">
              <label for="sort_order">Order</label>
              <select id="sort_order">
              <option value="desc">Most to Least</option>
              <option value="asc">Least to Most</option>
              </select>
            </div>
          <div class="field">
            <label>&nbsp;</label>
            <button id="apply">Apply Filters</button>
          </div>
        </div>

        <div class="preset-row">
          <button class="preset-button" data-preset="recruiting">Recruiting</button>
          <button class="preset-button" data-preset="completed">Completed</button>
          <button class="preset-button" data-preset="industry">Industry</button>
          <button class="preset-button" data-preset="largest">Largest Enrollment</button>
          <button class="preset-button" data-preset="reset">Reset View</button>
        </div>

        <div class="context-bar" id="explorer-context">
          <div class="context-copy" id="explorer-context-copy"></div>
          <button class="context-clear" id="clear-context" type="button">Clear Jump</button>
        </div>

        <div class="toolbar">
          <div id="results-summary">Loading trials...</div>
          <div class="pager">
            <div class="page-jump">
              <label for="page-number">Page</label>
              <input id="page-number" type="number" min="1" value="1" />
              <button id="go-page" type="button">Go</button>
            </div>
            <button id="prev-page" class="status" style="border:0; cursor:pointer;">Previous</button>
            <button id="next-page" class="status" style="border:0; cursor:pointer; margin-left:8px;">Next</button>
          </div>
        </div>

        <div class="table" id="trial-list"></div>
      </div>

      <div class="detail-card">
        <div class="status">Live Local View</div>
        <h3 id="detail-title">Select a trial</h3>
        <p class="detail-copy" id="detail-copy">
          Choose any row from the explorer to view a more readable summary of the structured trial record.
        </p>

        <div class="detail-grid">
          <div class="mini-card">
            <span>Status</span>
            <strong id="detail-status">--</strong>
          </div>
          <div class="mini-card">
            <span>Phase</span>
            <strong id="detail-phase">--</strong>
          </div>
          <div class="mini-card">
            <span>Enrollment</span>
            <strong id="detail-enrollment">--</strong>
          </div>
          <div class="mini-card">
            <span>Sites</span>
            <strong id="detail-sites">--</strong>
          </div>
        </div>

        <div class="section-title">Conditions</div>
        <div class="pill-row" id="detail-conditions"></div>

        <div class="section-title">Interventions</div>
        <div class="mini-list" id="detail-interventions"></div>

        <div class="section-title">Locations</div>
        <div class="mini-list" id="detail-locations"></div>
      </div>
    </section>

    <section class="section-shell" id="patterns">
      <div class="section-header">
        <div>
          <div class="section-kicker">Pattern Watch</div>
          <h2>Research Signals</h2>
          <p>These panels turn the local dataset into higher-level signals so a researcher or strategy team can move from records to patterns.</p>
        </div>
      </div>
    </section>

    <section class="analytics-grid">
      <div class="panel">
        <h2>Status Overview</h2>
        <p class="detail-copy" id="status-overview-copy">Loading status patterns...</p>
        <div class="leaders" id="status-overview-list"></div>
      </div>

      <div class="panel">
        <h2>Termination Risk by Phase</h2>
        <p class="detail-copy">A simple early-termination view across study phases in the current local dataset.</p>
        <div class="leaders" id="termination-phase-list"></div>
      </div>

      <div class="panel">
        <h2>Low-Coverage Conditions</h2>
        <p class="detail-copy">A heuristic list of conditions with low trial counts in the currently ingested data slice.</p>
        <div class="leaders" id="coverage-list"></div>
      </div>
    </section>

    <section class="section-shell" id="briefs">
      <div class="section-header">
        <div>
          <div class="section-kicker">Research Briefs</div>
          <h2>Drill Down by Sponsor or Condition</h2>
          <p>Use these panels when you want to move from broad leaderboards into a specific research area, institution, or company portfolio.</p>
        </div>
      </div>
    </section>

    <section class="research-grid">
      <div class="panel">
        <h2>Sponsor Research Brief</h2>
        <div class="controls" style="margin-bottom: 14px;">
          <div class="field" style="grid-column: span 3;">
            <label for="sponsor-drilldown">Sponsor Name</label>
            <input id="sponsor-drilldown" list="sponsor-suggestions" placeholder="GlaxoSmithKline" autocomplete="off" />
          </div>
          <div class="field">
            <label>&nbsp;</label>
            <button id="load-sponsor-brief">Load Sponsor</button>
          </div>
        </div>
        <p class="detail-copy" id="sponsor-brief-copy">Load a sponsor to inspect portfolio size, completion behavior, and top conditions.</p>
        <div class="detail-grid">
          <div class="mini-card"><span>Trials</span><strong id="sponsor-brief-trials">--</strong></div>
          <div class="mini-card"><span>Completion Rate</span><strong id="sponsor-brief-completion">--</strong></div>
          <div class="mini-card"><span>Terminated Early</span><strong id="sponsor-brief-terminated">--</strong></div>
          <div class="mini-card"><span>Avg Enrollment</span><strong id="sponsor-brief-enrollment">--</strong></div>
        </div>
        <div class="section-title">Top Conditions</div>
        <div class="leaders" id="sponsor-brief-conditions"></div>
        <div class="section-title">Phase Distribution</div>
        <div class="leaders" id="sponsor-brief-phases"></div>
      </div>

      <div class="panel">
        <h2>Condition Research Brief</h2>
        <div class="controls" style="margin-bottom: 14px;">
          <div class="field" style="grid-column: span 3;">
            <label for="condition-drilldown">Condition Name</label>
            <input id="condition-drilldown" list="condition-suggestions" placeholder="Delirium" autocomplete="off" />
          </div>
          <div class="field">
            <label>&nbsp;</label>
            <button id="load-condition-brief">Load Condition</button>
          </div>
        </div>
        <p class="detail-copy" id="condition-brief-copy">Load a condition to inspect recruitment activity, completion outcomes, and sponsor mix.</p>
        <div class="detail-grid">
          <div class="mini-card"><span>Trials</span><strong id="condition-brief-trials">--</strong></div>
          <div class="mini-card"><span>Recruiting</span><strong id="condition-brief-recruiting">--</strong></div>
          <div class="mini-card"><span>Completed</span><strong id="condition-brief-completed">--</strong></div>
          <div class="mini-card"><span>Early Termination</span><strong id="condition-brief-terminated">--</strong></div>
        </div>
        <div class="section-title">Sponsor Mix</div>
        <div class="leaders" id="condition-brief-sponsors"></div>
        <div class="section-title">Status Distribution</div>
        <div class="leaders" id="condition-brief-statuses"></div>
      </div>
    </section>
  </div>

  <datalist id="sponsor-suggestions"></datalist>
  <datalist id="condition-suggestions"></datalist>
  <datalist id="country-suggestions"></datalist>
  <datalist id="phase-suggestions"></datalist>

  <script>
    const state = {
      limit: 10,
      offset: 0,
      total: 0,
      selectedNctId: null,
      statusBucket: "",
    };

    const ids = (name) => document.getElementById(name);
    const suggestionTimers = new Map();

    function formatNumber(value) {
      if (value === null || value === undefined || value === "") return "--";
      return new Intl.NumberFormat().format(value);
    }

    function formatText(value) {
      return value ?? "--";
    }

    function formatLabel(value) {
      if (value === null || value === undefined || value === "") return "--";
      return String(value).replaceAll("_", " ");
    }

    function setFieldValue(id, value) {
      ids(id).value = value ?? "";
    }

    function resetExplorerFilters() {
      state.statusBucket = "";
      setFieldValue("status", "");
      setFieldValue("sponsor_type", "");
      setFieldValue("country", "");
      setFieldValue("condition", "");
      setFieldValue("sponsor", "");
      setFieldValue("phase", "");
      setFieldValue("min_enrollment", "");
      setFieldValue("sort_by", "last_update_posted");
      setFieldValue("sort_order", "desc");
      clearExplorerContext();
    }

    function clearExplorerContext() {
      state.statusBucket = "";
      ids("explorer-context").classList.remove("active");
      ids("explorer-context-copy").textContent = "";
    }

    function updateExplorerContext() {
      const parts = [];
      if (state.statusBucket) {
        parts.push(`Status group: ${formatLabel(state.statusBucket)}`);
      }
      if (ids("sponsor").value.trim()) {
        parts.push(`Sponsor: ${ids("sponsor").value.trim()}`);
      }
      if (ids("condition").value.trim()) {
        parts.push(`Condition: ${ids("condition").value.trim()}`);
      }
      if (ids("phase").value.trim()) {
        parts.push(`Phase: ${ids("phase").value.trim()}`);
      }

      if (!parts.length) {
        clearExplorerContext();
        return;
      }

      ids("explorer-context").classList.add("active");
      ids("explorer-context-copy").textContent = `Explorer focused on ${parts.join(" · ")}`;
    }

    async function jumpToTrials(filters = {}) {
      resetExplorerFilters();

      if ("status_bucket" in filters) {
        state.statusBucket = filters.status_bucket ?? "";
      }
      if ("status" in filters) {
        setFieldValue("status", filters.status ?? "");
      }
      if ("condition" in filters) {
        setFieldValue("condition", filters.condition ?? "");
      }
      if ("sponsor" in filters) {
        setFieldValue("sponsor", filters.sponsor ?? "");
      }
      if ("phase" in filters) {
        setFieldValue("phase", filters.phase ?? "");
      }
      if ("sponsor_type" in filters) {
        setFieldValue("sponsor_type", filters.sponsor_type ?? "");
      }
      if ("sort_by" in filters) {
        setFieldValue("sort_by", filters.sort_by ?? "last_update_posted");
      }
      if ("sort_order" in filters) {
        setFieldValue("sort_order", filters.sort_order ?? "desc");
      }

      state.offset = 0;
      state.selectedNctId = null;
      updateExplorerContext();
      await loadTrials();
      window.location.hash = "explorer";
      ids("explorer").scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function applyPreset(name) {
      if (name === "reset") {
        resetExplorerFilters();
        return;
      }

      if (name === "recruiting") {
        setFieldValue("status", "RECRUITING");
        setFieldValue("sort_by", "last_update_posted");
        setFieldValue("sort_order", "desc");
        return;
      }

      if (name === "completed") {
        setFieldValue("status", "COMPLETED");
        setFieldValue("sort_by", "last_update_posted");
        setFieldValue("sort_order", "desc");
        return;
      }

      if (name === "industry") {
        setFieldValue("sponsor_type", "Industry");
        setFieldValue("sort_by", "enrollment_count");
        setFieldValue("sort_order", "desc");
        return;
      }

      if (name === "largest") {
        setFieldValue("sort_by", "enrollment_count");
        setFieldValue("sort_order", "desc");
        return;
      }
    }

    function buildParams() {
      const params = new URLSearchParams();
      params.set("limit", String(state.limit));
      params.set("offset", String(state.offset));

      for (const field of ["status", "sponsor_type", "country", "condition", "sponsor", "phase", "min_enrollment", "sort_by", "sort_order"]) {
        const value = ids(field).value.trim();
        if (value) params.set(field, value);
      }

      if (state.statusBucket) {
        params.set("status_bucket", state.statusBucket);
      }

      return params;
    }

    async function getJson(path) {
      const response = await fetch(path);
      if (!response.ok) throw new Error(`Request failed: ${response.status}`);
      return response.json();
    }

    function renderSuggestions(targetId, suggestions) {
      const datalist = ids(targetId);
      datalist.innerHTML = "";
      for (const suggestion of suggestions) {
        const option = document.createElement("option");
        option.value = suggestion;
        datalist.appendChild(option);
      }
    }

    async function loadSuggestions(field, query, targetId) {
      const payload = await getJson(`/stats/autocomplete?field=${encodeURIComponent(field)}&q=${encodeURIComponent(query)}&limit=8`);
      renderSuggestions(targetId, payload.suggestions);
    }

    function attachAutosuggest(inputId, field, targetId) {
      const input = ids(inputId);
      input.addEventListener("input", () => {
        const query = input.value.trim();
        const existingTimer = suggestionTimers.get(inputId);
        if (existingTimer) {
          clearTimeout(existingTimer);
        }

        const timer = setTimeout(() => {
          loadSuggestions(field, query, targetId).catch((error) => console.error(error));
        }, 120);
        suggestionTimers.set(inputId, timer);
      });

      input.addEventListener("focus", () => {
        loadSuggestions(field, input.value.trim(), targetId).catch((error) => console.error(error));
      });
    }

    function renderTrials(payload) {
      state.total = payload.total;
      const start = payload.total === 0 ? 0 : payload.offset + 1;
      const end = payload.total === 0 ? 0 : payload.offset + payload.results.length;
      const pageNumber = payload.limit ? Math.floor(payload.offset / payload.limit) + 1 : 1;
      const totalPages = payload.limit ? Math.max(1, Math.ceil(payload.total / payload.limit)) : 1;
      ids("results-summary").textContent = `Showing ${start}-${end} of ${payload.total} matching trials · Page ${pageNumber} of ${totalPages}`;
      ids("page-number").value = String(pageNumber);
      ids("page-number").max = String(totalPages);
      ids("prev-page").classList.toggle("hidden", pageNumber <= 1);
      ids("next-page").classList.toggle("hidden", pageNumber >= totalPages);

      const container = ids("trial-list");
      container.innerHTML = "";

      if (!payload.results.length) {
        container.innerHTML = '<div class="empty">No trials matched the current filters.</div>';
        return;
      }

      for (const trial of payload.results) {
        const row = document.createElement("div");
        row.className = `trial-row${state.selectedNctId === trial.nct_id ? " active" : ""}`;
        row.dataset.nctId = trial.nct_id;
        row.innerHTML = `
          <div>
            <div class="trial-title">${trial.brief_title ?? trial.nct_id}</div>
            <div class="trial-meta">${trial.nct_id} · ${formatText(trial.status)} · ${formatText(trial.sponsor_name)}</div>
          </div>
          <div class="metric">
            <strong>${formatText(trial.phase)}</strong>
            <span>Phase</span>
          </div>
          <div class="metric">
            <strong>${formatNumber(trial.enrollment_count)}</strong>
            <span>Enrollment</span>
          </div>
          <div class="metric">
            <strong>${formatNumber(trial.location_count)}</strong>
            <span>Sites</span>
          </div>
        `;
        row.addEventListener("click", () => loadTrialDetail(trial.nct_id));
        container.appendChild(row);
      }
    }

    function syncActiveTrialRow() {
      document.querySelectorAll(".trial-row").forEach((row) => {
        row.classList.toggle("active", row.dataset.nctId === state.selectedNctId);
      });
    }

    function renderLeaders(targetId, items, formatter) {
      const container = ids(targetId);
      container.innerHTML = "";
      if (!items.length) {
        container.innerHTML = '<div class="empty">No data available.</div>';
        return;
      }
      for (const item of items) {
        const node = document.createElement("div");
        node.className = "leader";
        node.innerHTML = formatter(item);
        container.appendChild(node);
      }
    }

    function renderClickableLeaders(targetId, items, formatter, onClick) {
      const container = ids(targetId);
      container.innerHTML = "";
      if (!items.length) {
        container.innerHTML = '<div class="empty">No data available.</div>';
        return;
      }
      for (const item of items) {
        const node = document.createElement("button");
        node.type = "button";
        node.className = "leader clickable";
        node.innerHTML = formatter(item);
        node.addEventListener("click", () => onClick(item));
        container.appendChild(node);
      }
    }

    async function loadSponsorBrief(name) {
      const sponsorName = name || ids("sponsor-drilldown").value.trim();
      if (!sponsorName) return;

      try {
        const payload = await getJson(`/stats/sponsors/${encodeURIComponent(sponsorName)}`);
        ids("sponsor-drilldown").value = sponsorName;
        ids("sponsor-brief-copy").textContent = `${payload.sponsor_name} ran ${formatNumber(payload.trial_count)} trials in this local dataset.`;
        ids("sponsor-brief-trials").textContent = formatNumber(payload.trial_count);
        ids("sponsor-brief-completion").textContent = `${(payload.completion_rate * 100).toFixed(1)}%`;
        ids("sponsor-brief-terminated").textContent = `${formatNumber(payload.terminated_early_count)} (${(payload.terminated_early_rate * 100).toFixed(1)}%)`;
        ids("sponsor-brief-enrollment").textContent = formatNumber(payload.average_enrollment);

        renderClickableLeaders("sponsor-brief-conditions", payload.top_conditions, (item) => `
          <div>
            <strong>${item.label}</strong>
            <span>${formatNumber(item.trial_count)} trials</span>
          </div>
          <div><span>condition</span></div>
        `, async (item) => {
          await jumpToTrials({
            sponsor: payload.sponsor_name,
            condition: item.label,
            status: "",
            status_bucket: "",
            sort_by: "last_update_posted",
            sort_order: "desc",
          });
        });

        renderClickableLeaders("sponsor-brief-phases", payload.phase_distribution, (item) => `
          <div>
            <strong>${item.label}</strong>
            <span>${formatNumber(item.trial_count)} trials</span>
          </div>
          <div><span>phase</span></div>
        `, async (item) => {
          await jumpToTrials({
            sponsor: payload.sponsor_name,
            phase: item.label,
            status: "",
            status_bucket: "",
            sort_by: "last_update_posted",
            sort_order: "desc",
          });
        });
      } catch (error) {
        console.error(error);
        ids("sponsor-brief-copy").textContent = "That sponsor could not be loaded from the current dataset.";
        ids("sponsor-brief-conditions").innerHTML = '<div class="empty">No sponsor brief available.</div>';
        ids("sponsor-brief-phases").innerHTML = '<div class="empty">No sponsor brief available.</div>';
      }
    }

    async function loadConditionBrief(name) {
      const conditionName = name || ids("condition-drilldown").value.trim();
      if (!conditionName) return;

      try {
        const payload = await getJson(`/stats/conditions/${encodeURIComponent(conditionName)}`);
        ids("condition-drilldown").value = conditionName;
        ids("condition-brief-copy").textContent = `${payload.condition_name} appears in ${formatNumber(payload.trial_count)} trials in this local dataset.`;
        ids("condition-brief-trials").textContent = formatNumber(payload.trial_count);
        ids("condition-brief-recruiting").textContent = formatNumber(payload.recruiting_count);
        ids("condition-brief-completed").textContent = formatNumber(payload.completed_count);
        ids("condition-brief-terminated").textContent = `${formatNumber(payload.terminated_early_count)} (${(payload.terminated_early_rate * 100).toFixed(1)}%)`;

        renderClickableLeaders("condition-brief-sponsors", payload.sponsor_type_distribution, (item) => `
          <div>
            <strong>${item.label}</strong>
            <span>${formatNumber(item.trial_count)} trials</span>
          </div>
          <div><span>sponsor mix</span></div>
        `, async (item) => {
          await jumpToTrials({
            condition: payload.condition_name,
            sponsor_type: item.label,
            status: "",
            status_bucket: "",
            sort_by: "last_update_posted",
            sort_order: "desc",
          });
        });

        renderClickableLeaders("condition-brief-statuses", payload.status_distribution, (item) => `
          <div>
            <strong>${item.label}</strong>
            <span>${formatNumber(item.trial_count)} trials</span>
          </div>
          <div><span>status</span></div>
        `, async (item) => {
          await jumpToTrials({
            condition: payload.condition_name,
            status: item.label,
            status_bucket: "",
            sort_by: "last_update_posted",
            sort_order: "desc",
          });
        });
      } catch (error) {
        console.error(error);
        ids("condition-brief-copy").textContent = "That condition could not be loaded from the current dataset.";
        ids("condition-brief-sponsors").innerHTML = '<div class="empty">No condition brief available.</div>';
        ids("condition-brief-statuses").innerHTML = '<div class="empty">No condition brief available.</div>';
      }
    }

    async function loadSummaryPanels() {
      const [health, conditions, sponsors, trials] = await Promise.all([
        getJson("/health"),
        getJson("/stats/conditions?limit=3"),
        getJson("/stats/sponsors?limit=3"),
        getJson("/trials?limit=1"),
      ]);

      ids("stat-health").textContent = health.status.toUpperCase();
      ids("stat-total").textContent = formatNumber(trials.total);
      ids("stat-condition").textContent = conditions.results[0]?.condition_name ?? "--";
      ids("stat-sponsor").textContent = sponsors.results[0]?.sponsor_name ?? "--";

      if (sponsors.results[0]?.sponsor_name) {
        loadSponsorBrief(sponsors.results[0].sponsor_name);
      }

      if (conditions.results[0]?.condition_name) {
        loadConditionBrief(conditions.results[0].condition_name);
      }

      const analyticsResults = await Promise.allSettled([
        getJson("/stats/status-overview"),
        getJson("/stats/terminations/phases?limit=5"),
        getJson("/stats/coverage/conditions?limit=5&low_coverage_threshold=2"),
      ]);

      const [statusOverviewResult, phaseTerminationsResult, conditionCoverageResult] = analyticsResults;

      if (statusOverviewResult.status === "fulfilled") {
        const statusOverview = statusOverviewResult.value;
        ids("status-overview-copy").textContent =
          `${formatNumber(statusOverview.terminated_early_trials)} of ${formatNumber(statusOverview.total_trials)} trials ended early in this local dataset.`;

        renderClickableLeaders("status-overview-list", statusOverview.buckets, (item) => `
          <div>
            <strong>${item.status_bucket.replaceAll("_", " ")}</strong>
            <span>${formatNumber(item.trial_count)} trials</span>
          </div>
          <div><span>${(item.share_of_trials * 100).toFixed(1)}%</span></div>
        `, async (item) => {
          await jumpToTrials({
            status: "",
            status_bucket: item.status_bucket,
            sort_by: "last_update_posted",
            sort_order: "desc",
          });
        });
      } else {
        ids("status-overview-copy").textContent = "Status analytics are temporarily unavailable.";
        ids("status-overview-list").innerHTML = '<div class="empty">This panel could not load right now.</div>';
      }

      if (phaseTerminationsResult.status === "fulfilled") {
        renderClickableLeaders("termination-phase-list", phaseTerminationsResult.value.results, (item) => `
          <div>
            <strong>${item.group_name}</strong>
            <span>${formatNumber(item.trial_count)} trials</span>
          </div>
          <div><span>${(item.terminated_early_rate * 100).toFixed(1)}% early end</span></div>
        `, async (item) => {
          await jumpToTrials({
            phase: item.group_name,
            status: "",
            status_bucket: "terminated_early",
            sort_by: "last_update_posted",
            sort_order: "desc",
          });
        });
      } else {
        ids("termination-phase-list").innerHTML = '<div class="empty">Phase termination analytics are temporarily unavailable.</div>';
      }

      if (conditionCoverageResult.status === "fulfilled") {
        renderClickableLeaders("coverage-list", conditionCoverageResult.value.results, (item) => `
          <div>
            <strong>${item.condition_name}</strong>
            <span>${formatNumber(item.trial_count)} trials</span>
          </div>
          <div><span>${item.coverage_label.replaceAll("_", " ")}</span></div>
        `, async (item) => {
          await jumpToTrials({
            condition: item.condition_name,
            status: "",
            status_bucket: "",
            sort_by: "last_update_posted",
            sort_order: "desc",
          });
        });
      } else {
        ids("coverage-list").innerHTML = '<div class="empty">Coverage analytics are temporarily unavailable.</div>';
      }
    }

    async function loadTrials() {
      const payload = await getJson(`/trials?${buildParams().toString()}`);
      renderTrials(payload);
    }

    async function loadTrialDetail(nctId) {
      state.selectedNctId = nctId;
      syncActiveTrialRow();
      const payload = await getJson(`/trials/${nctId}`);

      ids("detail-title").textContent = payload.brief_title ?? payload.nct_id;
      ids("detail-copy").textContent = `${payload.nct_id} · ${formatText(payload.sponsor_name)} · ${formatLabel(payload.study_type)}`;
      ids("detail-status").textContent = formatLabel(payload.overall_status);
      ids("detail-phase").textContent = formatLabel(payload.phase);
      ids("detail-enrollment").textContent = formatNumber(payload.enrollment_count);
      ids("detail-sites").textContent = formatNumber(payload.summary.location_count);

      ids("detail-conditions").innerHTML = payload.conditions.length
        ? payload.conditions.map((condition) => `<span class="pill">${condition}</span>`).join("")
        : '<div class="empty">No conditions listed.</div>';

      ids("detail-interventions").innerHTML = payload.interventions.length
        ? payload.interventions.map((item) => `<div><strong>${formatText(item.intervention_type)}</strong> · ${item.intervention_name}</div>`).join("")
        : '<div class="empty">No interventions listed.</div>';

      ids("detail-locations").innerHTML = payload.locations.length
        ? payload.locations.slice(0, 6).map((item) => `<div><strong>${formatText(item.facility)}</strong> · ${[item.city, item.state, item.country].filter(Boolean).join(", ")}</div>`).join("")
        : '<div class="empty">No locations listed.</div>';
    }

    ids("apply").addEventListener("click", async () => {
      state.offset = 0;
      updateExplorerContext();
      await loadTrials();
    });

    ids("prev-page").addEventListener("click", async () => {
      state.offset = Math.max(0, state.offset - state.limit);
      await loadTrials();
    });

    ids("next-page").addEventListener("click", async () => {
      if (state.offset + state.limit < state.total) {
        state.offset += state.limit;
        await loadTrials();
      }
    });

    ids("go-page").addEventListener("click", async () => {
      const totalPages = Math.max(1, Math.ceil(state.total / state.limit));
      const requestedPage = Number.parseInt(ids("page-number").value, 10);
      if (Number.isNaN(requestedPage)) {
        ids("page-number").value = "1";
        return;
      }

      const safePage = Math.min(Math.max(requestedPage, 1), totalPages);
      state.offset = (safePage - 1) * state.limit;
      await loadTrials();
    });

    ids("page-number").addEventListener("keydown", async (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        ids("go-page").click();
      }
    });

    ids("load-sponsor-brief").addEventListener("click", async () => {
      await loadSponsorBrief();
    });

    ids("load-condition-brief").addEventListener("click", async () => {
      await loadConditionBrief();
    });

    ids("clear-context").addEventListener("click", async () => {
      clearExplorerContext();
      setFieldValue("status", "");
      setFieldValue("condition", "");
      setFieldValue("sponsor", "");
      setFieldValue("phase", "");
      setFieldValue("sponsor_type", "");
      state.offset = 0;
      updateExplorerContext();
      await loadTrials();
    });

    document.querySelectorAll("[data-preset]").forEach((node) => {
      node.addEventListener("click", async () => {
        applyPreset(node.dataset.preset);
        state.offset = 0;
        updateExplorerContext();
        await loadTrials();
        window.location.hash = "explorer";
      });
    });

    attachAutosuggest("country", "country", "country-suggestions");
    attachAutosuggest("condition", "condition", "condition-suggestions");
    attachAutosuggest("condition-drilldown", "condition", "condition-suggestions");
    attachAutosuggest("sponsor", "sponsor", "sponsor-suggestions");
    attachAutosuggest("sponsor-drilldown", "sponsor", "sponsor-suggestions");
    attachAutosuggest("phase", "phase", "phase-suggestions");

    Promise.all([loadSummaryPanels(), loadTrials()]).catch((error) => {
      console.error(error);
      ids("trial-list").innerHTML = '<div class="empty">The UI could not load data from the local API.</div>';
    });
  </script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    return HTMLResponse(content=HTML_PAGE)
