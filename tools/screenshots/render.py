import json, sys, html, os

PALETTE = {
 'black':'#3b4252','red':'#e06c75','green':'#98c379','brown':'#d19a66','yellow':'#e5c07b',
 'blue':'#61afef','magenta':'#c678dd','cyan':'#56b6c2','white':'#d8dee9','default':'#d8dee9',
}
BG = '#1e222a'

def color(v, default):
    if v in (None, 'default'):
        return default
    if v in PALETTE:
        return PALETTE[v]
    if len(v) == 6:
        return '#' + v
    return default

SCRUB = [' \u00b7 Claude Team', ' \u00b7 Claude Max', ' \u00b7 Claude Pro']
# SHOT_REPLACE 格式："原字串||替代字串"，用空白補齊長度差，避免格線跑掉
REPLACE = [pair.split('||') for pair in os.environ.get('SHOT_REPLACE', '').split(';;') if '||' in pair]

def scrub_row(row):
    txt = ''.join(c['c'] for c in row)
    for src, dst in REPLACE:
        idx = txt.find(src)
        if idx >= 0:
            padded = dst.ljust(len(src))[:len(src)]
            for i, ch in enumerate(padded):
                row[idx + i] = dict(row[idx + i], c=ch)
            txt = ''.join(c['c'] for c in row)
    for bad in SCRUB:
        idx = txt.find(bad)
        if idx >= 0:
            for i in range(idx, idx + len(bad)):
                row[i] = dict(row[i], c=' ')
            txt = ''.join(c['c'] for c in row)
    return row

def cells_to_html(path, drop_top=0, drop_bottom=0, trim_blank=True):
    d = json.load(open(path))
    d['cells'] = [scrub_row(r) for r in d['cells']]
    rows = d['cells'][drop_top: len(d['cells']) - drop_bottom if drop_bottom else None]
    if trim_blank:
        while rows and not ''.join(c['c'] for c in rows[-1]).strip():
            rows.pop()
    # 清掉寬字元誤判造成的溢位：整行分隔線後面多出來的 ─
    cleaned = []
    for row in rows:
        txt = ''.join(c['c'] for c in row).rstrip()
        # 分隔線因寬字元誤判而溢位到下一行時，去掉行首多餘的 ─
        if txt.startswith('─') and set(txt.rstrip()) != {'─'}:
            n = len(txt) - len(txt.lstrip('─'))
            row = row[n:]
        cleaned.append(row)
    rows = cleaned

    if os.environ.get('COLLAPSE_BLANK'):
        squeezed, blank = [], 0
        for row in rows:
            if ''.join(c['c'] for c in row).strip():
                blank = 0
                squeezed.append(row)
            else:
                blank += 1
                if blank <= int(os.environ['COLLAPSE_BLANK']):
                    squeezed.append(row)
        rows = squeezed

    out = []
    for row in rows:
        line, run, style = [], '', None
        for ch in row:
            st = (color(ch['fg'], '#d8dee9'), color(ch['bg'], BG), ch['b'])
            if st != style:
                if run:
                    line.append(span(run, style))
                run, style = '', st
            run += ('' if ch['c'] == '\ufffd' else ch['c'])
        if run:
            line.append(span(run, style))
        text = ''.join(line).rstrip()
        out.append(text or '&nbsp;')
    return '\n'.join(out)

def span(text, st):
    fg, bg, bold = st
    css = f'color:{fg}'
    if bg != BG:
        css += f';background:{bg}'
    if bold:
        css += ';font-weight:600'
    return f'<span style="{css}">{html.escape(text)}</span>'

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
  * {{ box-sizing: border-box; }}
  body {{ margin:0; padding:36px; background:#0f1115; }}
  .win {{ background:{bg}; border-radius:10px; overflow:hidden; box-shadow:0 18px 50px rgba(0,0,0,.55); }}
  .bar {{ height:30px; background:#2b303b; display:flex; align-items:center; padding:0 12px; gap:7px; }}
  .dot {{ width:11px; height:11px; border-radius:50%; }}
  .t {{ margin-left:10px; color:#8b93a5; font:12px -apple-system,sans-serif; }}
  pre {{ margin:0; padding:16px 18px; color:#d8dee9;
        font-family:"SF Mono","Menlo","DejaVu Sans Mono",monospace;
        font-size:14px; line-height:1.5; white-space:pre; }}
</style></head><body>
<div class="win">
  <div class="bar"><span class="dot" style="background:#ff5f57"></span>
  <span class="dot" style="background:#febc2e"></span>
  <span class="dot" style="background:#28c840"></span>
  <span class="t">{title}</span></div>
  <pre>{body}</pre>
</div></body></html>"""

if __name__ == '__main__':
    src, dst, title = sys.argv[1], sys.argv[2], sys.argv[3]
    drop_top = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    body = cells_to_html(src, drop_top=drop_top)
    open(dst, 'w').write(TEMPLATE.format(bg=BG, title=title, body=body))
    print('wrote', dst)
