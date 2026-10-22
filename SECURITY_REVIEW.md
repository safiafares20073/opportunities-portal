# Security Review — Opportunities Portal

**Scope:** Static application source from the approved mobile-filter release.
**Review date:** 22 October 2026
**Method:** Manual source inspection, targeted static regression checks, JavaScript syntax checks, and release smoke checks.

## Review findings and resolutions

| Area | Finding | Result |
|---|---|---|
| Dynamic content | Card and modal templates use `escapeHtml` for text and attribute values. No direct insertion of raw opportunity fields into HTML templates was identified in the inspected paths. | Existing encoding retained |
| Application links | The existing `https://` prefix test did not parse the full URL or reject embedded credentials. | Replaced with `safeOfficialUrl`: requires a valid absolute HTTPS URL with hostname and no embedded username/password, and uses HTML escaping at output |
| New tabs | Application-source links use `target="_blank"` with `rel="noopener noreferrer"`. | Existing protection retained |
| Service Worker | The previous fetch handler processed HTTP(S) requests without checking the requesting URL's origin. | Restricted fetch interception and caching to the portal's own origin |
| Browser storage | Favorites and visual preferences are stored locally. No server-side account or credential store exists in this application. | No change needed |
| Secrets and credentials | No obvious API key or password assignments identified in the release application source through targeted checks. | No credential requirement for the static site |
| Dependencies | Site runs on native HTML/CSS/JS and local JSON without third-party runtime script dependencies. | No dependency change |

## Verification

The release passes JavaScript syntax validation, the existing release smoke suite, and targeted security-regression checks for safe official URL handling, encoded dynamic content, link isolation, and same-origin Service Worker behavior.

**Limitations:** This review does not claim a penetration test, a live external-link security audit, or proof that every remote opportunity has the latest eligibility and deadline. The public deployment should be checked on GitHub Pages after publication.
