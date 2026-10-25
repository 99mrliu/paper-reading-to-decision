"""Count every UTF-8 file; reject unsupported conversions instead of omitting them."""
from pathlib import Path
import json,sys
root=Path(__file__).resolve().parent
rows=[];images=[]
for p in sorted(root.rglob('*')):
    if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts or p.suffix=='.pyc':continue
    name=str(p.relative_to(root));raw=p.read_bytes()
    if raw.startswith(b'\x89PNG\r\n\x1a\n'):
        images.append(name);continue
    if raw.startswith(b'%PDF') or p.suffix.lower()=='.ipynb':
        raise SystemExit('Explicit text extraction required: '+name)
    raw.decode('utf-8')
    if b'\x00' in raw:raise SystemExit('Unreliable text input: '+name)
    if len(raw)>2*1024**2:raise SystemExit('Oversized text file: '+name)
    rows.append({'path':name,'utf8_bytes':len(raw)})
total=sum(x['utf8_bytes'] for x in rows)
print(json.dumps({'status':'passed' if total<=245760 else 'over_limit',
    'text_bytes':total,'text_KiB':round(total/1024,3),'hard_limit':245760,
    'below_recommended_200_KiB':total<=204800,'remaining_hard_limit':245760-total,
    'images':images,'counted_files':len(rows),'files':rows},ensure_ascii=False,indent=2))
sys.exit(0 if total<=245760 else 1)
