# بوابة الفرص | Opportunities Portal

**Opportunities Portal for Yemeni Students** — a lightweight, bilingual web portal for discovering educational opportunities from official institutions. The released catalog contains **20 opportunities: 10 scholarships and 10 online courses**.

## Features | المميزات

- Arabic RTL and English LTR interface, with locally saved language selection.
- Light and dark themes with locally saved preference.
- Instant keyword search and combined filters for category, subject, country, and deadline status.
- Detailed opportunity view with eligibility, funding/benefits, deadline, and official source link.
- Favorites saved in browser `localStorage` across reloads.
- Same-origin Service Worker caching of application files and catalog to enable offline browsing after the initial online visit.
- Responsive layout for mobile and desktop screens.

## Technology

Semantic HTML5, CSS3, Vanilla JavaScript, JSON, localStorage, and Service Worker / Cache API. No production build step or third-party runtime packages.

## Run locally

From the project root:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/` in a modern browser. Run over HTTP localhost or HTTPS; opening `index.html` directly from a filesystem path is not supported for Service Worker features.

## Checks

```bash
python scripts/validate_data.py
python scripts/test_release_smoke.py
node --check js/app.js
node --check js/ui-preferences.js
node --check sw.js
```

The scripts verify structural constraints and JavaScript syntax. Manual browser checks are documented separately in `TEST_REPORT.md` with their testing method identified.

## Project documents

- `PROJECT_PROPOSAL.md` — original Phase 1 project proposal (historical planning scope).
- `DATA_GUIDE.md` — data-entry and source-verification guidance.
- `DATA_AUDIT.md` — canonical list of the 20 current records and their official source URLs.
- `TEST_REPORT.md` — validation and user-acceptance results.
- `SECURITY_REVIEW.md` — static-application security controls and review notes.
- `README_DEPLOY.md` — GitHub Pages publication and offline verification procedure.

**Data currency:** Funding figures shown in USD may be approximate conversions. Official institutions retain authority over their fees, eligibility, applications, and deadlines. The portal does not process applications or collect accounts or identity documents.
