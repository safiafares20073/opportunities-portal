# Project Proposal: Opportunities Portal for Yemeni Students

**Capstone Project** — Dr. Fadhl Alakwaa's Google Antigravity Student Guide  
**Author:** Safia Fares  
**Format:** One-Page Proposal (Phase 1)

---

## 1. Problem Statement & Target Users

### Problem Statement
Yemeni students and graduates face severe obstacles finding verified scholarships, free accredited courses, and internships. Available opportunities are dispersed across unvetted social media pages, plagued by expired or scam listings, and inaccessible under severe bandwidth limits, recurring power outages, and language barriers. Students need a centralized, verified, lightweight, and offline-ready web portal with a native Arabic interface to discover and track opportunities before deadlines lapse.

### Target Users
- **Yemeni Secondary & University Students:** Pursuing fully or partially funded regional and international scholarships.
- **Self-Directed Learners:** Seeking free accredited tech and professional courses, nanodegrees, and certifications.
- **Early-Career Graduates:** Searching for remote, local, or regional internships.
- **Context Constraints:** Budget smartphones, high data costs, and slow or intermittent 3G/4G connectivity.

---

## 2. User Stories

1. **US1 — Opportunity Discovery (Filtering):**  
   *As a Yemeni student,* I want to filter opportunities by study field, host country, and deadline urgency so that I can quickly narrow down relevant listings without full page reloads.  
   *Acceptance Criteria:* Client-side filter updates the visible cards immediately upon selection.

2. **US2 — Keyword Search:**  
   *As an applicant,* I want to search listings by title, provider, or topic in Arabic (and common English terms) so that I can instantly locate specific programs.  
   *Acceptance Criteria:* Real-time search matches partial strings across titles and organizations with sub-second response.

3. **US3 — Verified Opportunity Details:**  
   *As a student,* I want to view comprehensive eligibility rules, official source URLs, and verification dates in Arabic so that I can apply securely without falling for scams.  
   *Acceptance Criteria:* Detail view displays requirements, official domain link, and manual verification timestamp (`YYYY-MM-DD`).

4. **US4 — Arabic Deadline Urgency Badges:**  
   *As an applicant,* I want clear Arabic status badges ("متاحة", "تغلق قريبًا", "منتهية") so that I can prioritize urgent submissions.  
   *Acceptance Criteria:* Dynamic date evaluation labels opportunities as "متاحة" (Active), "تغلق قريبًا" (Closing soon, < 14 days), or "منتهية" (Expired) with color-coded tags.

5. **US5 — Favorites & Offline Bookmarking:**  
   *As a user with intermittent power and internet,* I want to save opportunities to my favorites so that I can review them anytime offline.  
   *Acceptance Criteria:* Bookmarked items persist in browser `localStorage` and remain accessible in the "Favorites" tab offline.

6. **US6 — Native Arabic RTL Interface:**  
   *As an Arabic speaker,* I want the portal to load natively in Arabic with natural Right-to-Left (RTL) orientation so that navigation and reading are comfortable.  
   *Acceptance Criteria:* Page defaults to `dir="rtl"` and `lang="ar"` with culturally aligned typography and layout.

---

## 3. MVP Features

- **Primary Arabic RTL Interface:** Fully implemented Arabic UI with native right-to-left alignment, utilizing CSS logical properties for clean layout symmetry.
- **Opportunity Listing:** Responsive card grid showing organization, field, Arabic deadline badge, and bookmark button.
- **Search & Multi-Filter Engine:** Instant client-side filtering by field, country, category, and deadline status.
- **Opportunity Details View:** Detailed modal presenting requirements, funding coverage, application link, and verification date.
- **Favorites System:** Client-side bookmarking stored in `localStorage` for offline reference.
- **Deadline Indicators:** Dynamic Arabic status badges ("متاحة", "تغلق قريبًا", "منتهية") calculated from local system date.
- **Mobile Responsiveness:** Touch-friendly, lightweight layout styled for low-spec smartphones and low bandwidth.
- **Offline Access:** Service Worker and client-side caching enabling access to cached listings and saved favorites without an active connection.

---

## 4. Stretch Goals & Out-of-Scope (Version 1)

### Optional Stretch Goals
- **English LTR & Language Switcher:** Interactive toggle and complete English UI translation. (Data schema and CSS logical properties remain architecturally ready for future activation).

### Out-of-Scope (Version 1)
- User accounts, server-side authentication, and cloud profile sync.
- Backend server framework, dynamic database (e.g., PostgreSQL/MongoDB), or server-side API.
- Direct in-app application submission or document uploading.
- Automated web scrapers or ingestion bots.
- User comments, discussion forums, or peer mentoring chat.
- Push notification servers or SMS alert systems.

---

## 5. Proposed Technology Stack

- **Markup:** HTML5 semantic markup configured with `dir="rtl"` and `lang="ar"`.
- **Styles:** Vanilla CSS3 using CSS logical properties (`margin-inline`, `padding-inline`, `text-align: start`) for native RTL and effortless future LTR support.
- **Logic:** Vanilla JavaScript (ES6+, modular, zero runtime dependencies) for instant client-side filtering and offline state handling.
- **Data Layer:** Local structured JSON file (`opportunities.json`) with bilingual schema keys (`title_ar`, `title_en`, etc.).
- **Offline / Storage:** Browser `localStorage` for favorites and Service Worker / Cache API for offline readiness.

---

## 6. Data Quality & Verification Requirements

- **Minimum Catalog:** At least **20 real, active, or recurring opportunities** relevant to Yemeni youth (Scholarships, Free Courses, Internships).
- **Manual Verification Standard:** Every listing must be manually verified against an official institutional source URL.
- **Required Metadata Schema:** `id`, `title_ar`, `title_en`, `organization`, `category` (Scholarship/Course/Internship), `field`, `country`, `coverage`, `deadline` (ISO Date or Rolling), `official_url`, `verification_date` (`YYYY-MM-DD`), `eligibility_ar`, and `eligibility_en`.
