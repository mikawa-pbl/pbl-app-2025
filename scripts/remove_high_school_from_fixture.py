import json
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'shiokara' / 'fixtures' / 'company_reviews.json'
text = p.read_text(encoding='utf-8')
data = json.loads(text)
changed = False
for obj in data:
    fields = obj.get('fields', {})
    if 'high_school' in fields:
        del fields['high_school']
        changed = True
if changed:
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Removed high_school from fixtures')
else:
    print('No high_school fields found')
