# Implementation Plan: Opportunities Portal Project Proposal

## Goal Description
Prepare a comprehensive, one-page `PROJECT_PROPOSAL.md` in English for the Capstone project **"Opportunities Portal"** (from Dr. Fadhl Alakwaa's Google Antigravity student guide). The web application aims to empower Yemeni students to discover verified scholarships, free certified courses, and internship opportunities under low-bandwidth and offline conditions, supporting both Arabic (RTL) and English (LTR).

This plan outlines the structure, content, and verification requirements for `PROJECT_PROPOSAL.md` prior to creating the file.

---

## User Review Required

> [!IMPORTANT]
> **No Application Code Execution**: As requested, this phase is strictly restricted to crafting `PROJECT_PROPOSAL.md`. No application code, package installations, or external dependencies will be created.

> [!NOTE]
> **RTL & Bilingual UI Scope**: The proposal will explicitly detail how the interface accommodates Arabic RTL and English LTR without backend overhead, utilizing CSS logical properties and client-side locale state switching.

---

## Proposed Changes

### Documentation

#### [NEW] `PROJECT_PROPOSAL.md` (in `c:\Users\DELL\Documents\opportunities-portal\PROJECT_PROPOSAL.md`)
The file will be structured into the following sections:

1. **Project Title & Executive Summary**
   - Title: Opportunities Portal for Yemeni Students
   - Core objective: Bridging the information gap for Yemeni youth seeking global and regional academic and career advancements.

2. **Problem Statement & Target Users**
   - **Problem Statement**: Yemeni students face unique hurdles: internet fragmentation, slow/expensive data, scam or outdated listings on social media groups, and language hurdles.
   - **Target Audience & Personas**:
     - *High School Graduates & University Students*: Seeking undergraduate/graduate scholarships.
     - *Self-Taught Learners & Tech Enthusiasts*: Seeking free accredited online courses & nanodegrees.
     - *Early Career Professionals & Interns*: Seeking remote or regional internships.

3. **User Stories (Testable & Formatted with Acceptance Criteria)**
   - **US1: Opportunity Browsing & Filter**: As a student, I want to filter opportunities by type (scholarship, course, internship), field, country, and deadline so that I can quickly find relevant options.
   - **US2: Keyword Search**: As an applicant, I want to search titles, organizations, and fields by keyword so I can locate specific programs immediately.
   - **US3: Detail View & Source Verification**: As an applicant, I want to view detailed eligibility criteria, official source links, and verification dates so that I can apply with confidence and avoid fraudulent listings.
   - **US4: Deadline Urgency Indicators**: As a student, I want to see clear, color-coded visual indicators for closing deadlines (e.g., `< 7 days`, `Open`, `Closed`) so I can prioritize urgent applications.
   - **US5: Bookmarking / Favorites**: As a user with intermittent power/internet, I want to save opportunities to my favorites list stored locally on my device so I can revisit them anytime.
   - **US6: Bilingual & RTL/LTR Switcher**: As an Arabic speaker, I want to switch between Arabic (RTL) and English (LTR) seamlessly without losing my current search or filter state.
   - **US7: Offline Access**: As a student in areas with unstable connectivity, I want previously viewed opportunities to load even when offline so I can review requirements without an active connection.

4. **MVP Feature Specifications**
   - **Opportunity Listing**: Responsive card grid with tags, organization logo/badges, deadline status, and quick bookmark button.
   - **Search & Multi-Filter Engine**: Client-side filtering by opportunity type, study field, host country, and deadline window.
   - **Opportunity Details View**: Modal or dedicated view showing full description, stipend/coverage, eligibility, application instructions, official source URL, and verification stamp.
   - **Favorites System**: LocalStorage-backed bookmarking mechanism.
   - **Deadline Indicators**: Dynamic calculation of days remaining with visual badges (e.g., Red: `< 7 days`, Amber: `< 14 days`, Green: `Active`, Grey: `Closed`).
   - **Mobile Responsiveness**: Lightweight, touch-friendly UI optimized for small screens and budget smartphones.
   - **Offline Capability**: Progressive Web App (PWA) / Service Worker caching or LocalStorage caching of `opportunities.json`.
   - **Bilingual Interface**: Arabic (RTL) and English (LTR) toggle with JSON-driven localization.

5. **Out-of-Scope for MVP (Phase 1)**
   - User authentication / server-side account management.
   - Cloud database and backend server APIs (Node.js/Python/Express/Django/SQL).
   - In-app direct application submission / form filling.
   - Automated web scraping / crawling bots.
   - User comments, forums, reviews, or peer-to-peer mentoring chat.
   - Real-time SMS or push notification servers.

6. **Proposed Technology Stack**
   - **Frontend Markup**: HTML5 (semantic, accessible, WAI-ARIA compliant).
   - **Styling**: Vanilla CSS3 (CSS custom properties, CSS Grid & Flexbox, CSS logical properties for seamless RTL support `margin-inline-start`, etc.).
   - **Scripting**: Modern Vanilla JavaScript (ES6+ modular script, async/await, Fetch API, no heavy framework overhead to ensure fast loading on 2G/3G networks).
   - **Data Layer**: Local JSON file (`data/opportunities.json`).
   - **Offline Storage**: Service Worker with Cache API and browser `localStorage`.

7. **Data Quality & Verification Requirement**
   - Baseline dataset of **at least 20 real opportunities** relevant to Yemeni applicants.
   - Standardized opportunity schema:
     - `id`: Unique identifier (string/slug).
     - `title_en` & `title_ar`: Opportunity title in English and Arabic.
     - `organization`: Hosting entity / university / platform.
     - `category`: `Scholarship` | `Course` | `Internship`.
     - `field`: e.g., Computer Science, Engineering, Medicine, Business, Humanities.
     - `coverage`: Fully Funded, Partially Funded, Tuition Waiver, Free with Certificate.
     - `target_country` / `location`: Country or Online/Remote.
     - `deadline`: ISO 8601 Date (`YYYY-MM-DD`).
     - `official_url`: Canonical official application or announcement URL.
     - `verification_date`: Date verified by reviewer (`YYYY-MM-DD`).
     - `verified_by`: Name or verification tag.
     - `requirements`: Brief eligibility summary.

---

## Verification Plan

### Automated Checks
- Verify Markdown formatting and structural integrity of `PROJECT_PROPOSAL.md`.
- Verify word count, section presence, and syntax using a non-destructive script or view tool.

### Manual Verification
- Confirm all 6 specific prompt requirements are satisfied:
  1. Problem statement & target users clearly defined.
  2. At least five clear, testable user stories with acceptance criteria.
  3. MVP features list (listing, search, filters, details, favorites, deadline indicators, mobile responsiveness, offline access).
  4. Out-of-scope features clearly delineated.
  5. Proposed stack specified (HTML, CSS, JS, local JSON).
  6. Data quality requirement specified (>= 20 real opportunities, official URLs, verification dates).
  7. Arabic RTL and English support incorporated.
