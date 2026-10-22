# Verification and User Acceptance Report

**Project:** Opportunities Portal
**Release reviewed:** V8, 22 October 2026
**Catalog:** 20 records (10 scholarships, 10 online courses)

## 1. Automated structural checks

| Check | Scope | Recorded result |
|---|---|---|
| `scripts/validate_data.py` | JSON structure, required fields, formats and record count | PASS (20 records) |
| `scripts/test_release_smoke.py` | Release file presence, categories, identifiers, URLs and app-feature markers | PASS |
| `node --check js/app.js` | JavaScript syntax | PASS |
| `node --check js/ui-preferences.js` | Language/theme helper syntax | PASS |
| `node --check sw.js` | Service Worker syntax | PASS |

*Method:* Source-level automated checks. These checks do not constitute a full browser integration test or a live examination of every provider website.

## 2. User acceptance observations

The project owner reported the following hands-on checks of the V8 application running locally:

| Functional area | Observation |
|---|---|
| Opportunity links and deadline labels | Opened the catalog links and compared displayed dates with the referenced source pages |
| Search and filters | Interacted with filters and observed updated opportunity cards |
| Favorites persistence | Saved items remained present after closing and reopening the page repeatedly |
| Language selection | Verified English interface behavior after the V8 translation corrections |
| Theme control | Dark mode responded correctly |
| Responsive layout | Used Chrome device emulation at 360 CSS pixels and observed no clipped content or horizontal scrolling |

*Method:* Owner-reported manual acceptance observations, distinguished from recorded automated browser instrumentation.

## 3. Deployment acceptance procedure

For GitHub Pages publication, use `README_DEPLOY.md`: verify the public URL and application assets under HTTPS, visit online once to populate the service-worker cache, then switch the browser to Offline and reload the page to check cached catalog and favorites. Record public-URL test results when deployment is performed.

## 4. Historical development test record

The original Antigravity milestone logs document search, filtering, details-modal and `localStorage` favorites tests. A historical Chrome headless viewport measurement of **440 CSS px** should not be described as a strict 360 CSS px automated test. The separate V8 manual Chrome device-emulation check at 360 CSS px is recorded above.
