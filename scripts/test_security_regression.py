"""Focused static security regression for the Opportunities Portal."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
app=(ROOT/'js/app.js').read_text(encoding='utf-8')
sw=(ROOT/'sw.js').read_text(encoding='utf-8')
checks={
 'HTML encoding of dynamic data': all(p in app for p in ['function escapeHtml(', '.replace(/&/g', '.replace(/</g', '.replace(/"/g']),
 'strict HTTPS parsing': all(p in app for p in ['function safeOfficialUrl(', 'new URL(value)', "url.protocol !== 'https:'", 'url.username || url.password']),
 'escaped link output': 'escapeHtml(safeOfficialUrl(item.official_url))' in app,
 'external tab isolation': 'rel="noopener noreferrer"' in app,
 'Service Worker same-origin restriction': 'url.origin !== self.location.origin' in sw,
 'Service Worker caches site assets': all(x in sw for x in ['js/ui-preferences.js', 'data/opportunities.json']),
}
for name,ok in checks.items():print(('PASS' if ok else 'FAIL')+' '+name)
raise SystemExit(not all(checks.values()))
