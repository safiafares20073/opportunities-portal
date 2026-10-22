# Source Register | Opportunity Data Audit

**Dataset edition:** 22 October 2026
**Catalog:** 20 unique records (10 scholarships, 10 online courses)
**Source of record:** `data/opportunities.json`

Each entry below mirrors the title, stored deadline and URL from the released JSON dataset. Institution websites provide the authoritative current rules; the source register is not a guarantee of acceptance or enrollment.

## Scholarships

1. **Emile Boutmy Undergraduate Scholarship 2027** — Deadline: `2027-01-13` — [Official page](https://www.sciencespo.fr/students/en/fees-funding/bursaries-financial-aid/emile-boutmy-scholarship/)
2. **Emile Boutmy Masters Scholarship 2027** — Deadline: `2026-11-29` — [Official page](https://www.sciencespo.fr/students/en/fees-funding/bursaries-financial-aid/emile-boutmy-scholarship/)
3. **UBC International Scholars Program 2027** — Deadline: `2026-11-15` — [Official page](https://undergraduatescholarships.ubc.ca/prog/2027_international_scholars_program_application/)
4. **Ingram Scholars Program 2027** — Deadline: `2026-12-01` — [Official page](https://www.vanderbilt.edu/scholarships/ingram/)
5. **Cornelius Vanderbilt Scholarship 2027** — Deadline: `2026-12-01` — [Official page](https://www.vanderbilt.edu/scholarships/signature/)
6. **Yenching Academy Scholarship 2027** — Deadline: `2026-11-30` — [Official page](https://yenchingacademy.pku.edu.cn/ADMISSIONS.htm)
7. **IMPRS Intelligent Systems Funded PhD 2027** — Deadline: `2026-11-15` — [Official page](https://imprs.is.mpg.de/news/imprs-is-now-accepting-applications-for-2027)
8. **IMPRS Astrophysics Munich PhD 2027** — Deadline: `2026-11-01` — [Official page](https://application.imprs-astro.mpg.de/)
9. **IMPRS Astronomy and Cosmic Physics Heidelberg PhD 2027** — Deadline: `2026-11-03` — [Official page](https://www.imprs-hd.mpg.de/3192/Application)
10. **UBC International Major Entrance Scholarship (IMES)** — Deadline: `2027-01-15` — [Official page](https://apply.educationplannerbc.ca/apply/institution/ubc/539E2475-0215-44C3-A4D0-EA806CF9AB9F)

## Online courses

1. **Python Essentials 1** — Deadline: `Rolling` — [Official page](https://www.netacad.com/courses/python-essentials-1)
2. **Python Essentials 2** — Deadline: `Rolling` — [Official page](https://www.netacad.com/courses/python-essentials-2)
3. **Introduction to Cybersecurity** — Deadline: `Rolling` — [Official page](https://www.netacad.com/courses/introduction-to-cybersecurity)
4. **Endpoint Security** — Deadline: `Rolling` — [Official page](https://www.netacad.com/courses/endpoint-security)
5. **Operating Systems Basics** — Deadline: `Rolling` — [Official page](https://www.netacad.com/courses/operating-systems-basics)
6. **Data Analytics Essentials** — Deadline: `Rolling` — [Official page](https://www.netacad.com/courses/data-analytics-essentials)
7. **Responsive Web Design Certification** — Deadline: `Rolling` — [Official page](https://www.freecodecamp.org/learn/2022/responsive-web-design/)
8. **Relational Databases Certification** — Deadline: `Rolling` — [Official page](https://www.freecodecamp.org/learn/relational-database/)
9. **CS50x 2026: Introduction to Computer Science** — Deadline: `Rolling` — [Official page](https://cs50.harvard.edu/x/)
10. **CS50 Introduction to Cybersecurity** — Deadline: `Rolling` — [Official page](https://cs50.harvard.edu/cybersecurity/)

## Verification method

Catalog fields, unique IDs, URL schemes and date formats are checked by `scripts/validate_data.py`. Opportunity links and listed dates were also checked by the project owner during the October 2026 release review. Enrollment and eligibility are governed by each linked official page. `Rolling` denotes an ongoing/no fixed closing date in the dataset, not a promise that enrollment is available at every moment.

### Distinct application pathways

- **UBC International Scholars Program:** separate scholarship application and school nomination, as described by the official application portal.
- **UBC International Major Entrance Scholarship (IMES):** merit consideration through the undergraduate admission process, not the International Scholars nomination pathway.
- **Python Essentials 1 and 2:** distinct Cisco Networking Academy course pages.
