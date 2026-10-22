# Security Audit Report: Opportunities Portal

**Project:** Opportunities Portal — بوابة الفرص  
**Audit date:** 22 October 2026  
**Mode:** Read-Only Security Audit  
**Scope:** Static web application (`index.html`, `css/style.css`, `js/app.js`, `js/ui-preferences.js`, `sw.js`, `data/opportunities.json`, `test-harness.html`, and automated tests).

> **Evidence note:** This document preserves the findings and test results reported by the Antigravity audit provided by the project owner. It is a record of that audit, not a claim of an additional independent test run. No files were changed during the reported audit.

## 1. Executive Summary

| Category | Reported status | Summary evidence |
|---|---|---|
| XSS (Cross-Site Scripting) | PASS | Dynamic template values are HTML-escaped; bilingual text updates use text nodes. |
| Exposed secrets | PASS | No exposed credentials, API keys, private keys, or authentication tokens identified in the inspected project. |
| External dependencies | PASS | No external CDNs, third-party runtime scripts, remote fonts, or CSS `@import` rules reported. |
| HTTPS links and tab isolation | PASS | All 20 production URLs use HTTPS; outbound links use `safeOfficialUrl()` and `rel="noopener noreferrer"`. |
| Browser storage (`localStorage`) | PASS | Stores favorites and interface preferences rather than credentials or personal data; storage failures are handled. |
| Service Worker security | PASS | Registration is restricted to HTTPS/localhost; fetch interception is restricted to same-origin requests. |

## 2. Detailed Findings and Evidence

### 2.1 Cross-Site Scripting (XSS)

- **HTML escaping:** `js/app.js` uses `escapeHtml()` (reported lines 388–397) to encode `&`, `<`, `>`, `"`, and `'`.
- **Dynamic templates:** In `buildModalHTML()` and `createCardElement()`, inspected dataset fields, including titles, organization, field, country, coverage, deadline, eligibility, verification date, and IDs, are passed through `escapeHtml()`.
- **CSS classes:** `categoryInfo.className` and `deadlineInfo.badgeClass` are derived from internal constants rather than opportunity data.
- **Bilingual interface:** `js/ui-preferences.js` updates text through `TreeWalker` and `node.nodeValue` instead of interpreting translated text as HTML.

**Reported finding:** No unescaped, attacker-controlled opportunity data was identified in the inspected rendering paths.

### 2.2 Exposed Secrets and Credentials

- Searches for terms such as `api_key`, `secret`, `token`, `password`, `bearer`, and `private_key` did not identify exposed credentials in inspected project files.
- `.gitignore` includes exclusions for common sensitive files, including `.env`, `*.key`, `*.pem`, `credentials.json`, and `secrets/`.

**Reported finding:** No exposed secrets were detected by the performed checks.

### 2.3 External Dependencies

- No externally loaded runtime scripts, remote fonts, CDN dependencies, or CSS `@import` rules were identified.
- The runtime application uses local HTML, CSS, JavaScript, and JSON assets.

**Reported finding:** The inspected application adheres to the project's zero-CDN requirement.

### 2.4 HTTPS Links and Tab Isolation

The `safeOfficialUrl()` function in `js/app.js` was reported to:

- Reject non-string values and control characters.
- Require the `https:` protocol and a valid hostname.
- Reject URLs containing embedded usernames or passwords.
- Return `#` for rejected inputs.

The audit reported HTTPS source URLs for **20/20 production opportunity records** and **8/8 test fixtures**. Outbound links opened in a new tab use `rel="noopener noreferrer"`.

**Reported finding:** URL validation and new-tab protections are in place. This structural check does **not** establish that every remote link leads directly to the intended current opportunity or that its deadline remains accurate.

### 2.5 Browser Storage (`localStorage`)

| Storage key | Purpose | Stored values |
|---|---|---|
| `opportunities_portal_favorites` | Saved opportunities | Array of opportunity IDs |
| `opportunities_portal_language` | Language preference | `ar` or `en` |
| `opportunities_portal_theme` | Theme preference | `light` or `dark` |

The audit reported defensive error handling around storage access and no storage of credentials, authentication tokens, or personal information.

### 2.6 Service Worker Security

- Service Worker registration in `js/app.js` is guarded for HTTPS or local loopback hosts.
- The fetch handler in `sw.js` restricts interception to the application's origin:

```javascript
if (url.origin !== self.location.origin) return;
```

- Older `opportunities-portal-*` caches are removed during activation.

**Reported finding:** External scholarship sites are not intercepted or cached by the project's Service Worker.

## 3. Comparison with `SECURITY_REVIEW.md`

| Previously documented area | Auditor observation |
|---|---|
| Dynamic content escaping | Confirmed; audit additionally reviewed text-node updates in `ui-preferences.js`. |
| Official link validation | Confirmed active `safeOfficialUrl()` checks. |
| New-tab protection | Confirmed `noopener noreferrer`. |
| Service Worker origin restriction | Confirmed same-origin check. |
| Local browser storage | Confirmed non-sensitive values and defensive handling. |
| Exposed credentials | None detected in the inspected source. |
| External dependencies | No external runtime dependencies detected. |

**Additional observations:** A Content Security Policy (CSP) and optional CSS-class sanitization are possible defense-in-depth improvements, not findings requiring immediate remediation in this audit. Documentation could explicitly mention the safe text-node handling in `ui-preferences.js`.

## 4. Reported Test Results

| Check | Reported outcome |
|---|---|
| JavaScript syntax validation | 0 syntax errors |
| `python scripts/test_security_regression.py` | **6/6 PASS** |
| `python scripts/test_release_smoke.py` | **11/11 PASS** |
| `python scripts/validate_data.py` | **20/20 structurally valid records** |

Security regression cases were reported to cover HTML encoding, HTTPS parsing, escaped links, external-tab isolation, same-origin Service Worker restrictions, and asset caching.

## 5. Limitations and Audit Record

- This was a **read-only review**: no application files were edited, packages installed, or commits created during the reported audit.
- The findings do not constitute a penetration test or a live verification of all remote scholarship links, eligibility requirements, and deadlines.
- Describing the audit as read-only does not independently prove that the Antigravity agent was technically restricted to read-only tools; its permission settings should be documented separately if required for assessment.
- Earlier remediation is documented in the project's existing `SECURITY_REVIEW.md` and associated source history. This report records the later verification, not a second remediation event.

**Overall reported result:** PASS for the six inspected security areas, subject to the limitations above.
