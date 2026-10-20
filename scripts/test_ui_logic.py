#!/usr/bin/env python3
"""
Test Suite: Opportunities Portal UI Logic & Filter Engine
==========================================================
Tests deadline calculation, Arabic text normalization, search matching,
multi-criteria filtering, and production dataset safety.
"""

import datetime
import json
import re
import sys
from pathlib import Path


def calculate_deadline_status(deadline_str: str, reference_date: datetime.date = None):
    """
    Port of client-side deadline calculation logic:
    - 'Rolling' -> 'متاحة'
    - days_remaining < 0 -> 'منتهية'
    - 0 <= days_remaining <= 14 -> 'تغلق قريبًا'
    - days_remaining > 14 -> 'متاحة'
    """
    if reference_date is None:
        reference_date = datetime.date.today()

    if deadline_str == "Rolling":
        return {
            "status": "متاحة",
            "badge_class": "status-active",
            "label": "متاحة (مستمرة)",
        }

    try:
        deadline_date = datetime.date.fromisoformat(deadline_str)
    except ValueError:
        return {
            "status": "غير محدد",
            "badge_class": "status-unknown",
            "label": "تاريخ غير صالح",
        }

    delta_days = (deadline_date - reference_date).days

    if delta_days < 0:
        return {
            "status": "منتهية",
            "badge_class": "status-expired",
            "label": "منتهية",
            "days_remaining": delta_days,
        }
    elif delta_days <= 14:
        return {
            "status": "تغلق قريبًا",
            "badge_class": "status-closing",
            "label": f"تغلق قريبًا ({delta_days} يوم)",
            "days_remaining": delta_days,
        }
    else:
        return {
            "status": "متاحة",
            "badge_class": "status-active",
            "label": "متاحة",
            "days_remaining": delta_days,
        }


def normalize_arabic(text: str) -> str:
    """Normalize Arabic text by removing diacritics and unifying characters."""
    if not text:
        return ""
    text = text.lower()
    # Remove Arabic tashkeel (diacritics)
    text = re.sub(r"[\u064B-\u0652\u0670]", "", text)
    # Unify Alef forms
    text = re.sub(r"[إأآا]", "ا", text)
    # Unify Yeh / Alef Maksura
    text = re.sub(r"[يى]", "ي", text)
    # Unify Teh Marbuta and Heh
    text = re.sub(r"[ةه]", "ه", text)
    return text.strip()


def matches_search(item: dict, query: str) -> bool:
    """Check if opportunity matches search query across Arabic & English fields."""
    if not query:
        return True
    norm_query = normalize_arabic(query)
    searchable_fields = [
        item.get("title_ar", ""),
        item.get("title_en", ""),
        item.get("organization", ""),
        item.get("field", ""),
        item.get("country", ""),
        item.get("eligibility_ar", ""),
        item.get("eligibility_en", ""),
    ]
    combined = " ".join(normalize_arabic(f) for f in searchable_fields)
    return norm_query in combined


def filter_dataset(items, query="", category="", field="", country="", status="", ref_date=None):
    """Filter list of opportunities by query and all dropdown criteria."""
    results = []
    for item in items:
        # Keyword search
        if query and not matches_search(item, query):
            continue
        # Category filter
        if category and item.get("category") != category:
            continue
        # Field filter
        if field and item.get("field") != field:
            continue
        # Country filter
        if country and item.get("country") != country:
            continue
        # Status filter
        if status:
            calc = calculate_deadline_status(item.get("deadline", ""), ref_date)
            if calc["status"] != status:
                continue
        results.append(item)
    return results


def run_tests():
    print("=" * 65)
    print("Opportunities Portal — Milestone 1 UI Logic Tests")
    print("=" * 65)
    ref_date = datetime.date(2026, 10, 16)
    failures = []

    # 1. Deadline Calculation Tests
    print("\n[Test 1] Deadline Calculation Logic:")
    cases = [
        ("Rolling", "متاحة", "status-active"),
        ("2026-11-20", "متاحة", "status-active"),    # 35 days remaining > 14
        ("2026-10-22", "تغلق قريبًا", "status-closing"), # 6 days remaining <= 14
        ("2026-10-20", "تغلق قريبًا", "status-closing"), # 4 days remaining <= 14
        ("2024-03-31", "منتهية", "status-expired"),   # Past date
    ]
    for dl, exp_status, exp_class in cases:
        res = calculate_deadline_status(dl, ref_date)
        if res["status"] == exp_status and res["badge_class"] == exp_class:
            print(f"  PASS: {dl:12} -> {res['status']} ({res['badge_class']})")
        else:
            failures.append(f"Deadline test failed for {dl}: got {res}, expected {exp_status}")
            print(f"  FAIL: {dl:12} -> got {res['status']}, expected {exp_status}")

    # 2. Arabic Normalization Tests
    print("\n[Test 2] Arabic Normalization & BiDi Search:")
    search_cases = [
        ("حاسوب", True, "Should match 'علوم الحاسوب' with exact keyword"),
        ("حاسوب", True, "Should match 'حاسوب' normalized"),
        ("مهارات Google", True, "Should match mixed Arabic/English brand name"),
        ("python", True, "Should match English keyword 'Python' case-insensitively"),
        ("غير_موجود_قطعا", False, "Should not match nonexistent term"),
    ]
    sample_item = {
        "title_ar": "البرنامج التأسيسي لتعليم الذكاء الاصطناعي وبايثون",
        "title_en": "Google Foundation in AI and Python Programming",
        "organization": "مهارات Google للشرق الأوسط",
        "field": "علوم الحاسوب والذكاء الاصطناعي",
    }
    for q, should_match, desc in search_cases:
        matched = matches_search(sample_item, q)
        if matched == should_match:
            print(f"  PASS: Query '{q}' -> match={matched} ({desc})")
        else:
            failures.append(f"Search test failed for '{q}': got {matched}, expected {should_match}")
            print(f"  FAIL: Query '{q}' -> got {matched}, expected {should_match}")

    # 3. Test Fixtures Filtering Tests
    print("\n[Test 3] Fixture Dataset Multi-Criteria Filtering:")
    repo_root = Path(__file__).resolve().parent.parent
    fixtures_file = repo_root / "tests" / "fixtures" / "test-opportunities.json"
    with open(fixtures_file, "r", encoding="utf-8") as f:
        fixtures = json.load(f)

    print(f"  Loaded {len(fixtures)} test fixtures.")

    # All fixtures
    all_res = filter_dataset(fixtures, ref_date=ref_date)
    assert len(all_res) == 8, f"Expected 8 items, got {len(all_res)}"
    print(f"  PASS: No filters -> 8/8 returned")

    # Filter by category: Scholarship
    scholarships = filter_dataset(fixtures, category="Scholarship", ref_date=ref_date)
    assert len(scholarships) == 3, f"Expected 3 scholarships, got {len(scholarships)}"
    print(f"  PASS: Category='Scholarship' -> 3/8 returned")

    # Filter by category: Course + Status: متاحة
    courses_active = filter_dataset(fixtures, category="Course", status="متاحة", ref_date=ref_date)
    assert len(courses_active) == 3, f"Expected 3 active courses, got {len(courses_active)}"
    print(f"  PASS: Category='Course' + Status='متاحة' -> 3 returned")

    # Filter by status: تغلق قريبًا
    closing_soon = filter_dataset(fixtures, status="تغلق قريبًا", ref_date=ref_date)
    assert len(closing_soon) == 2, f"Expected 2 closing soon, got {len(closing_soon)}"
    print(f"  PASS: Status='تغلق قريبًا' -> 2 returned (UNDP & Remote Frontend)")

    # Filter by status: منتهية
    expired = filter_dataset(fixtures, status="منتهية", ref_date=ref_date)
    assert len(expired) == 1, f"Expected 1 expired, got {len(expired)}"
    print(f"  PASS: Status='منتهية' -> 1 returned (DAAD expired)")

    # Search + Category filter combined
    combined_res = filter_dataset(fixtures, query="الذكاء الاصطناعي", category="Course", ref_date=ref_date)
    assert len(combined_res) >= 1, "Expected at least 1 match"
    print(f"  PASS: Query='الذكاء الاصطناعي' + Category='Course' -> {len(combined_res)} returned")

    # Search with zero match (Empty state condition)
    empty_res = filter_dataset(fixtures, query="xyzNonExistentString123", ref_date=ref_date)
    assert len(empty_res) == 0, f"Expected 0 matches, got {len(empty_res)}"
    print(f"  PASS: Nonexistent query returns 0 items (triggers empty state)")

    # 4. Production Dataset Purity Check
    print("\n[Test 4] Production Dataset Purity (Zero Fabrication):")
    prod_file = repo_root / "data" / "opportunities.json"
    with open(prod_file, "r", encoding="utf-8") as f:
        prod_data = json.load(f)

    if prod_data == []:
        print("  PASS: data/opportunities.json is strictly [] (Zero fake data present).")
    else:
        failures.append("Production data file is not empty!")
        print(f"  FAIL: data/opportunities.json contains {len(prod_data)} items!")

    print("\n" + "=" * 65)
    if failures:
        print(f"[FAILED] {len(failures)} test(s) failed.")
        for fail in failures:
            print(f"  - {fail}")
        return 1
    else:
        print("[SUCCESS] All UI logic and filtering tests passed flawlessly.")
        return 0


if __name__ == "__main__":
    sys.exit(run_tests())
