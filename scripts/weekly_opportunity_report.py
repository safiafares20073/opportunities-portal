"""Read-only weekly deadline and stale-verification report for Opportunities Portal."""
import json
from pathlib import Path
from datetime import date

path = Path(__file__).resolve().parents[1] / 'data' / 'opportunities.json'
records = json.loads(path.read_text(encoding='utf-8'))
today = date.today()
print(f'Opportunities Portal read-only report | {today.isoformat()} | {len(records)} records')
print('\nClosing within 14 days:')
for item in records:
    value = item.get('deadline', 'Rolling')
    try:
        days = (date.fromisoformat(value) - today).days
    except (ValueError, TypeError):
        continue
    if 0 <= days <= 14:
        print(f'  {item["id"]}: {days} day(s), {value} | {item["official_url"]}')
print('\nReview dates older than 90 days / not independently confirmed:')
for item in records:
    value = item.get('verification_date', '')
    try:
        old = (today - date.fromisoformat(value)).days > 90
    except (ValueError, TypeError):
        old = True
    if old or item.get('verification_method') == 'original_dataset_unverified_manual_stamp':
        print(f'  {item["id"]}: {value or "missing"} | {item.get("review_status", "unknown")}')
