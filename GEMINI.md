# Project Rules: Opportunities Portal

These rules define strict development guidelines, safety protocols, and quality standards for the **Opportunities Portal** capstone project. All agents and contributors operating in this workspace must adhere to them at all times.

---

## 1. Workspace Boundaries & File Safety
- **Strict Working Directory**: Operate exclusively within the `opportunities-portal` directory (`c:\Users\DELL\Documents\opportunities-portal`). Never read, edit, or traverse files outside this workspace.
- **No Destructive Commands**: Never delete files, remove directories, or run destructive commands without explicit user review and written approval.
- **Secrets & Credentials Protection**: Never access, inspect, commit, or expose secret keys, API credentials, passwords, or `.env` files.

## 2. Technology & Architectural Constraints
- **Zero CDN Dependencies**: Use native HTML5, CSS3, and vanilla JavaScript only. All stylesheets, scripts, icons, and assets must be hosted locally within the project. External script/style CDNs are strictly prohibited.
- **Mobile-First Arabic RTL Interface**:
  - The interface must be designed mobile-first, maintaining full responsiveness and flawless layout at 360px minimum viewport width.
  - The primary document layout must be strictly Right-to-Left (`dir="rtl"`, `lang="ar"`).
- **CSS Logical Properties**: Always use modern CSS logical properties (`margin-inline`, `padding-inline`, `text-align: start`, `inset-inline`) to preserve clean geometry and future-proof the codebase.
- **Future LTR Readiness Without Overengineering**: Keep data schemas bilingual and styles logically symmetric for potential future English LTR support. Do **not** implement a language switcher or secondary UI in the current version.

## 3. Data Integrity & Verification Standards
- **Zero Fabrication Policy**: Never invent, hallucinate, or fabricate scholarships, training courses, internships, application deadlines, eligibility criteria, or provider details.
- **Mandatory Verification**: Every real opportunity must have:
  1. An official institutional source URL (`official_url`).
  2. An explicit manual verification date (`verification_date` in `YYYY-MM-DD` format).
- **Arabic Urgency Badges**: Deadline status labels must be rendered strictly in Arabic:
  - `"متاحة"` (Active)
  - `"تغلق قريبًا"` (Closing soon, < 14 days)
  - `"منتهية"` (Expired)

## 4. Development & Workflow Protocols
- **Review Before Major Changes**: Always propose a structured plan and request user approval before initiating major structural, architectural, or code changes.
- **Testing & Verification**: Execute thorough verification steps (including responsiveness, BiDi text rendering, and accessibility) after each task.
- **Git Milestone Commits**: After completing each milestone and verifying its stability, propose a clear, conventional Git commit message for user review.
