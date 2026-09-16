from pathlib import Path
import re, struct
root=Path(__file__).resolve().parents[1]
issues=[]
for day in range(1,31):
 d=root/'images'/f'day-{day:02}'
 article=root/'articles'/f'day-{day:02}.md'
 expected=['cover.png','core-workflow.png','recap.png']
 for name in expected:
  p=d/name
  if not p.exists(): issues.append(f'missing {p.relative_to(root)}'); continue
  if p.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n': issues.append(f'not png {p.relative_to(root)}')
  else:
   w,h=struct.unpack('>II',p.read_bytes()[16:24])
   if w/h < 1.7 or w/h > 1.8: issues.append(f'not 16:9 {p.relative_to(root)} {w}x{h}')
 text=article.read_text() if article.exists() else ''
 refs=re.findall(r'!\[[^]]*\]\((\.\./images/day-\d{2}/[^)]+\.png)\)',text)
 if len(refs)!=3: issues.append(f'day-{day:02} article image refs={len(refs)}')
if issues:
 print('\n'.join(issues)); raise SystemExit(1)
print('30 days × 3 PNG images passed file and article-reference checks')
