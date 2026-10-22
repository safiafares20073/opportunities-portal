"""Dependency-free prepublish checks for Opportunities Portal.
Run: python scripts/test_release_smoke.py
"""
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/opportunities.json').read_text(encoding='utf-8'))
errors=[]
def check(label,condition):
 print(('PASS' if condition else 'FAIL')+' '+label)
 if not condition: errors.append(label)
check('20 opportunities',len(data)>=20)
check('10 scholarships',sum(x.get('category')=='Scholarship' for x in data)==10)
check('10 courses',sum(x.get('category')=='Course' for x in data)==10)
ids=[x.get('id') for x in data]
check('unique IDs',len(ids)==len(set(ids)))
check('official HTTPS URLs',all(x.get('official_url','').startswith('https://') for x in data))
html=(ROOT/'index.html').read_text(encoding='utf-8');js=(ROOT/'js/app.js').read_text(encoding='utf-8');sw=(ROOT/'sw.js').read_text(encoding='utf-8')
check('Arabic RTL',bool(re.search(r'<html[^>]*lang="ar"[^>]*dir="rtl"|<html[^>]*dir="rtl"[^>]*lang="ar"',html)))
check('service-worker registration', 'serviceWorker.register' in js)
check('service-worker app shell', 'opportunities.json' in sw and 'index.html' in sw)
check('localStorage favorites', 'localStorage' in js)
check('opportunities data file referenced', 'opportunities.json' in js)
check('all release files present', all((ROOT/f).is_file() for f in ['index.html','css/style.css','js/app.js','sw.js','README.md','data/opportunities.json']))
print(f'RESULT: {len(errors)} failure(s). These checks do not verify live admissions or browser interactions.')
sys.exit(bool(errors))
