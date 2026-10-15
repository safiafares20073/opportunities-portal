#!/usr/bin/env python3
"""
Opportunities Portal Data Validator
====================================
Validates opportunities.json against schema, data integrity rules,
HTTPS official sources, date correctness, and verified entry requirements.
Uses only Python standard library.
"""

import datetime
import json
import re
import sys
import urllib.parse
from pathlib import Path

REQUIRED_FIELDS = [
    "id",
    "title_ar",
    "title_en",
    "organization",
    "category",
    "field",
    "country",
    "coverage",
    "deadline",
    "official_url",
    "verification_date",
    "eligibility_ar",
    "eligibility_en",
]

ALLOWED_CATEGORIES = {"Scholarship", "Course", "Internship"}
ID_PATTERN = re.compile(r"^[a-z0-9-]+$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MIN_REQUIRED_OPPORTUNITIES = 20


def is_valid_calendar_date(date_str: str) -> bool:
    """Check if string is a valid ISO calendar date (YYYY-MM-DD)."""
    if not DATE_PATTERN.match(date_str):
        return False
    try:
        datetime.date.fromisoformat(date_str)
        return True
    except (ValueError, TypeError):
        return False


def is_valid_https_url(url_str: str) -> bool:
    """Validate that URL has https scheme and a non-empty network location."""
    if not isinstance(url_str, str) or not url_str.startswith("https://"):
        return False
    try:
        parsed = urllib.parse.urlparse(url_str)
        return parsed.scheme == "https" and bool(parsed.netloc)
    except Exception:
        return False


def validate_opportunities(data_path: Path):
    """Validate opportunities JSON file and print detailed report."""
    print("=" * 65)
    print("Opportunities Portal — Dataset Validation")
    print(f"File: {data_path}")
    print("=" * 65)

    if not data_path.exists():
        print(f"[ERROR] Data file not found: {data_path}")
        return 1

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        print(f"[ERROR] Invalid JSON syntax: {err}")
        return 1
    except Exception as err:
        print(f"[ERROR] Failed to read data file: {err}")
        return 1

    if not isinstance(data, list):
        print("[ERROR] Top-level data structure must be a JSON array ([]).")
        return 1

    total_records = len(data)
    errors = []
    seen_ids = set()
    today = datetime.date.today()

    for idx, item in enumerate(data, start=1):
        record_id = item.get("id") if isinstance(item, dict) else f"item_{idx}"
        prefix = f"Record #{idx} [{record_id}]"

        if not isinstance(item, dict):
            errors.append(f"{prefix}: Must be a JSON object, got {type(item).__name__}")
            continue

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in item:
                errors.append(f"{prefix}: Missing required field '{field}'")
            elif item[field] is None:
                errors.append(f"{prefix}: Field '{field}' cannot be null")
            elif isinstance(item[field], str) and not item[field].strip():
                errors.append(f"{prefix}: Field '{field}' cannot be empty")

        # Validate ID
        if "id" in item and isinstance(item["id"], str):
            item_id = item["id"].strip()
            if not ID_PATTERN.match(item_id):
                errors.append(
                    f"{prefix}: Invalid ID format '{item_id}'. Must be lowercase alphanumeric with hyphens (e.g., 'chevening-2026')."
                )
            if item_id in seen_ids:
                errors.append(f"{prefix}: Duplicate ID '{item_id}' detected.")
            else:
                seen_ids.add(item_id)

        # Validate category
        if "category" in item and isinstance(item["category"], str):
            if item["category"] not in ALLOWED_CATEGORIES:
                errors.append(
                    f"{prefix}: Invalid category '{item['category']}'. Allowed: {sorted(ALLOWED_CATEGORIES)}"
                )

        # Validate deadline
        if "deadline" in item and isinstance(item["deadline"], str):
            dl = item["deadline"].strip()
            if dl != "Rolling" and not is_valid_calendar_date(dl):
                errors.append(
                    f"{prefix}: Invalid deadline '{dl}'. Must be 'Rolling' or ISO date (YYYY-MM-DD)."
                )

        # Validate official URL
        if "official_url" in item and isinstance(item["official_url"], str):
            url = item["official_url"].strip()
            if not is_valid_https_url(url):
                errors.append(
                    f"{prefix}: Invalid official_url '{url}'. Must be a valid URL starting with 'https://'."
                )

        # Validate verification date
        if "verification_date" in item and isinstance(item["verification_date"], str):
            vdate_str = item["verification_date"].strip()
            if not is_valid_calendar_date(vdate_str):
                errors.append(
                    f"{prefix}: Invalid verification_date '{vdate_str}'. Must be ISO date (YYYY-MM-DD)."
                )
            else:
                vdate = datetime.date.fromisoformat(vdate_str)
                if vdate > today:
                    errors.append(
                        f"{prefix}: verification_date '{vdate_str}' is in the future. Today is {today}."
                    )

    # Print validation errors if any
    if errors:
        print("\n[VALIDATION FAILED] The following integrity errors were found:")
        for err in errors:
            print(f"  * {err}")
        print(f"\nTotal Errors: {len(errors)}")
        return 1

    print("\n[PASSED] Structure & Field Validation: OK")
    print(f"  * JSON Syntax: Valid")
    print(f"  * Field Types & Patterns: Valid")
    print(f"  * Official HTTPS Sources: Valid")
    print(f"  * Date Formats & Verification Stamps: Valid")
    print(f"  * Total Records Evaluated: {total_records}")

    print("\n" + "-" * 65)
    print("Catalog Completeness Check:")
    if total_records >= MIN_REQUIRED_OPPORTUNITIES:
        print(
            f"[SUCCESS] Dataset meets requirement: {total_records}/{MIN_REQUIRED_OPPORTUNITIES} verified opportunities."
        )
    else:
        print(
            f"[PENDING] Minimum required: {MIN_REQUIRED_OPPORTUNITIES} verified opportunities."
        )
        print(f"          Current count   : {total_records}")
        print(
            f"          Status          : Structure is valid, but the minimum of {MIN_REQUIRED_OPPORTUNITIES} verified opportunities has not yet been met."
        )
    print("-" * 65)

    return 0


def main():
    repo_root = Path(__file__).resolve().parent.parent
    data_file = repo_root / "data" / "opportunities.json"

    if len(sys.argv) > 1:
        data_file = Path(sys.argv[1])

    exit_code = validate_opportunities(data_file)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
