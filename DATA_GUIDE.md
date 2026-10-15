# Opportunities Portal — Data Verification & Entry Guide

This guide defines the standards and workflow for manually entering and verifying educational, training, and internship opportunities for the **Opportunities Portal**.

---

## 1. Core Data Integrity Principles

1. **Zero Fabrication Policy**: Never invent, guess, or copy unverified opportunities from social media posts. Every listing must represent an authentic, verifiable program.
2. **Official Institutional Source**: Every opportunity must link directly to an official portal (`official_url`) hosted on the institution's official domain (`.edu`, `.gov`, `.org`, or official corporate domain). Aggregator, blog, or social media links are prohibited.
3. **Manual Verification Date**: Every record must be manually reviewed against the live official website and stamped with the exact date of verification (`verification_date` in `YYYY-MM-DD` format).
4. **HTTPS Protocol**: All source URLs must use secure HTTPS (`https://`).
5. **Bilingual Completeness**: Both Arabic and English titles and eligibility criteria must be filled in accurately.

---

## 2. Opportunity Schema Reference

Each record in `data/opportunities.json` is a JSON object with the following 13 required fields:

| Field | Type | Format / Allowed Values | Description & Example |
| :--- | :--- | :--- | :--- |
| `id` | string | `^[a-z0-9-]+$` | Unique lowercase slug. *Example:* `"chevening-scholarship-2026"` |
| `title_ar` | string | Non-empty | Arabic opportunity title. *Example:* `"منحة تشيفنينغ للدراسات العليا"` |
| `title_en` | string | Non-empty | English opportunity title. *Example:* `"Chevening Master's Scholarship"` |
| `organization` | string | Non-empty | Host entity / university. *Example:* `"UK Foreign, Commonwealth and Development Office"` |
| `category` | string | `"Scholarship"` \| `"Course"` \| `"Internship"` | Standardized category. |
| `field` | string | Non-empty | Study/career area. *Example:* `"All Academic Fields"` |
| `country` | string | Non-empty | Host country or `"Online"`. *Example:* `"United Kingdom"` |
| `coverage` | string | Non-empty | Funding type. *Example:* `"Fully Funded"` |
| `deadline` | string | `YYYY-MM-DD` or `"Rolling"` | ISO deadline date or `"Rolling"` for open programs. |
| `official_url` | string | `https://...` | Direct link to official application/announcement page. |
| `verification_date` | string | `YYYY-MM-DD` | Date when you manually checked the official page. |
| `eligibility_ar` | string | Non-empty | Key eligibility summary in Arabic. |
| `eligibility_en` | string | Non-empty | Key eligibility summary in English. |

---

## 3. Step-by-Step Verification & Entry Workflow

1. **Source Discovery**: Identify a candidate scholarship, course, or internship from a reputable educational partner, foundation, or university.
2. **Institutional Verification**:
   - Navigate to the official domain of the offering organization.
   - Verify that Yemeni nationals/students are eligible.
   - Check the confirmed application deadline.
   - Confirm funding/coverage terms.
3. **Record Entry**:
   - Open `data/opportunities.json`.
   - Append the new opportunity object following the schema above.
   - Set `verification_date` to today's date (`YYYY-MM-DD`).
4. **Run Data Validation**:
   - Execute the project validation script:
     ```powershell
     python scripts/validate_data.py
     ```
   - Confirm that all records pass validation and review progress toward the 20-opportunity capstone requirement.
