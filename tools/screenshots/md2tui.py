# 把 claude -p 的 markdown 輸出重繪成 Claude Code TUI 畫面
import html, re, sys, unicodedata

WIDTH = int(__import__('os').environ.get('SHOT_WIDTH_CHARS', 96))
C = {'dim':'#6b7280','text':'#d8dee9','bold':'#ffffff','user':'#9aa4b8',
     'accent':'#e0836a','green':'#98c379','cyan':'#61afef','muted':'#8b93a5'}

def w(s):
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)

def wrap(text, width, indent=''):
    lines, cur = [], ''
    for ch in text:
        if w(cur) + w(ch) > width:
            lines.append(cur)
            cur = indent + ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines

def inline(text):
    out, i = [], 0
    for part in re.split(r'(\*\*.+?\*\*)', text):
        if part.startswith('**') and part.endswith('**'):
            out.append(f'<span style="color:{C["bold"]};font-weight:600">{html.escape(part[2:-2])}</span>')
        else:
            out.append(f'<span style="color:{C["text"]}">{html.escape(part)}</span>')
    return ''.join(out)

def strip_md(text):
    return re.sub(r'\*\*(.+?)\*\*', r'\1', text)


def render_table(rows):
    """markdown 表格改用 HTML table 排版，避免 CJK 等寬字型對齊誤差"""
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    cells = [r for r in cells if not all(set(c) <= set('-: ') for c in r)]
    if not cells:
        return []
    head, body = cells[0], cells[1:]
    th = ''.join(f'<th>{inline_plain(strip_md(c), c)}</th>' for c in head)
    trs = ''.join('<tr>' + ''.join(f'<td>{inline_plain(strip_md(c), c)}</td>' for c in r) + '</tr>'
                  for r in body)
    return [f'<table class="md"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>']


def render_md(md):
    out = []
    lines = md.split('\n')
    i = 0
    while i < len(lines):
        raw = lines[i]
        i += 1
        line = raw.rstrip()
        if line.lstrip().startswith('```'):
            block = []
            while i < len(lines) and not lines[i].lstrip().startswith('```'):
                block.append(lines[i].rstrip())
                i += 1
            i += 1  # 跳過結尾圍籬
            out.append('')
            for b in block:
                out.append(f'  <span style="color:{C["cyan"]}">{html.escape(b)}</span>')
            out.append('')
            continue
        if line.lstrip().startswith('|') and line.rstrip().endswith('|'):
            block = [line]
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                block.append(lines[i])
                i += 1
            out.append('')
            out.extend(render_table(block))
            out.append('')
            continue
        if line.strip() == '---':
            out.append('')
            continue
        if line.startswith('#'):
            title = strip_md(line.lstrip('#').strip())
            out.append('')
            out.append(f'  <span style="color:{C["bold"]};font-weight:600">{html.escape(title)}</span>')
            out.append('')
            continue
        if line.startswith('- '):
            body = line[2:]
            segs = wrap(strip_md(body), WIDTH - 4, '')
            for n, seg in enumerate(segs):
                prefix = f'  <span style="color:{C["accent"]}">-</span> ' if n == 0 else '    '
                out.append(prefix + inline_plain(seg, body if n == 0 else ''))
            continue
        if not line.strip():
            out.append('')
            continue
        segs = wrap(strip_md(line), WIDTH - 2)
        for seg in segs:
            out.append('  ' + inline_plain(seg, line))
    return out

def inline_plain(seg, source):
    # 依原始 markdown 的 ** 標記，為片段內出現的粗體字串上色
    bolds = re.findall(r'\*\*(.+?)\*\*', source)
    esc = html.escape(seg)
    for b in bolds:
        eb = html.escape(b)
        if eb in esc:
            esc = esc.replace(eb, f'</span><span style="color:{C["bold"]};font-weight:600">{eb}</span><span style="color:{C["text"]}">', 1)
    return f'<span style="color:{C["text"]}">{esc}</span>'

import os
PROMPT = os.environ.get('SHOT_PROMPT', '（未提供提示詞）')
SHOWN_PATH = os.environ.get('SHOT_PATH', '~/Documents/flowboard-claude-skills')
ELAPSED = os.environ.get('SHOT_ELAPSED', '43s')
NEXT_HINT = os.environ.get('SHOT_NEXT', '{NEXT_HINT}')
WIN_TITLE = os.environ.get('SHOT_TITLE', 'flowboard-claude-skills — claude')

HEAD = f"""<span style="color:{C['accent']}"> ▐▛███▛█ </span>  <span style="color:{C['bold']};font-weight:600">Claude Code</span> <span style="color:{C['dim']}">v2.1.273</span>
<span style="color:{C['accent']}">▝▜██████▀</span>  <span style="color:{C['dim']}">Opus 5 with medium effort</span>
<span style="color:{C['accent']}">  ▝▝ ▝▝   </span>  <span style="color:{C['dim']}">{SHOWN_PATH}</span>
"""

TAIL = f"""
<span style="color:{C['muted']}">✻ Sautéed for {ELAPSED} · done</span>
<span style="color:{C['dim']}">{'─' * WIDTH}</span>
<span style="color:{C['accent']}">❯</span> <span style="color:{C['dim']}">{NEXT_HINT}</span>
<span style="color:{C['dim']}">{'─' * WIDTH}</span>
  <span style="color:#e5c07b">⏵⏵ auto mode on</span> <span style="color:{C['dim']}">(shift+tab to cycle)</span>"""

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
 body {{ margin:0; padding:36px; background:#0f1115; }}
 .win {{ background:#1e222a; border-radius:10px; overflow:hidden; box-shadow:0 18px 50px rgba(0,0,0,.55); }}
 .bar {{ height:30px; background:#2b303b; display:flex; align-items:center; padding:0 12px; gap:7px; }}
 .dot {{ width:11px; height:11px; border-radius:50%; }}
 .t {{ margin-left:10px; color:#8b93a5; font:12px -apple-system,sans-serif; }}
 table.md {{ border-collapse:collapse; margin:2px 0 6px 16px; font-size:13px; }}
 table.md th {{ text-align:left; padding:1px 22px 5px 0; color:#ffffff; font-weight:600;
                border-bottom:1px solid #3b4252; white-space:nowrap; }}
 table.md td {{ text-align:left; padding:3px 22px 3px 0; vertical-align:top; }}
 pre {{ margin:0; padding:16px 18px; color:#d8dee9;
       font-family:"SF Mono","Menlo",monospace; font-size:13.5px; line-height:1.55; white-space:pre; }}
</style></head><body><div class="win">
 <div class="bar"><span class="dot" style="background:#ff5f57"></span>
 <span class="dot" style="background:#febc2e"></span>
 <span class="dot" style="background:#28c840"></span>
 <span class="t">{title}</span></div>
 <pre>{body}</pre></div></body></html>"""

if __name__ == '__main__':
    md = open(sys.argv[1]).read().strip()
    limit = sys.argv[3] if len(sys.argv) > 3 else None
    if limit:
        md = md.split(limit)[0].rstrip().rstrip('-').rstrip()
    body = [HEAD]
    for ln in PROMPT.split('\n'):
        body.append(f'<span style="color:{C["accent"]}">❯</span> <span style="color:{C["user"]}">{html.escape(ln)}</span>'
                    if ln == PROMPT.split('\n')[0] else
                    f'  <span style="color:{C["user"]}">{html.escape(ln)}</span>')
    body.append('')
    rendered = render_md(md)
    first = next(i for i, l in enumerate(rendered) if l.strip())
    rendered[first] = f'<span style="color:{C["green"]}">⏺</span>' + rendered[first][1:]
    body.extend(rendered)
    # 連續空行壓成一行
    squeezed = []
    for ln in body:
        if ln.strip() == '' and squeezed and squeezed[-1].strip() == '':
            continue
        squeezed.append(ln)
    body = squeezed
    body.append(TAIL)
    open(sys.argv[2], 'w').write(TEMPLATE.format(body='\n'.join(body), title=html.escape(WIN_TITLE)))
    print('wrote', sys.argv[2], 'lines', len(body))
