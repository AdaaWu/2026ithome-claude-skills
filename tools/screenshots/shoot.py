#!/usr/bin/env python3
"""產出 Claude Code 操作截圖。

兩種模式：
  menu   以 pty 驅動真實 TUI，抓斜線指令選單畫面
  answer 以 claude -p 取得輸出，再重繪成 TUI 版面
"""
import argparse, contextlib, fcntl, json, os, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
VENV = os.environ.get('SHOT_VENV', '')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PY = os.path.join(VENV, 'bin', 'python') if VENV else sys.executable


SLOTS = int(os.environ.get('SHOT_SLOTS', 3))
LOCK_DIR = os.path.join(tempfile.gettempdir(), 'shoot-slots')


@contextlib.contextmanager
def claude_slot():
    """限制同機同時執行的 claude -p 數量，避免多條產線互相拖垮"""
    os.makedirs(LOCK_DIR, exist_ok=True)
    handles = [open(os.path.join(LOCK_DIR, f'slot-{i}'), 'w') for i in range(SLOTS)]
    held = None
    try:
        while held is None:
            for h in handles:
                try:
                    fcntl.flock(h, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    held = h
                    break
                except BlockingIOError:
                    continue
            if held is None:
                time.sleep(3)
        yield
    finally:
        if held is not None:
            fcntl.flock(held, fcntl.LOCK_UN)
        for h in handles:
            h.close()


def chrome_shot(html_path, png_path, width, height):
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=2', f'--window-size={width},{height}',
                    f'--screenshot={png_path}', html_path],
                   check=True, capture_output=True)


def estimate_height(html_path):
    body = open(html_path).read()
    lines = body.count('\n') - 12
    return max(200, int(lines * 20.9) + 150)


def mode_menu(args, work):
    steps = [{'send': 'claude\n'}, {'wait': 14},
             {'send': args.slash}, {'wait': 3}, {'snap': os.path.join(work, 'cells.json')}]
    steps_path = os.path.join(work, 'steps.json')
    json.dump(steps, open(steps_path, 'w'))
    cols = max(80, int((args.page_width - 72) / 8.13))
    env = dict(os.environ, SHOT_ROWS=str(args.rows), SHOT_COLS=str(cols))
    with claude_slot():
        subprocess.run([PY, os.path.join(HERE, 'drive.py'), args.project, steps_path],
                       check=True, env=env, capture_output=True)
    html_path = os.path.join(work, 'shot.html')
    env['COLLAPSE_BLANK'] = '1'
    subprocess.run([PY, os.path.join(HERE, 'render.py'), os.path.join(work, 'cells.json'),
                    html_path, args.title, '1'], check=True, env=env, capture_output=True)
    chrome_shot(html_path, args.out, args.page_width, args.height or estimate_height(html_path))


def mode_answer(args, work):
    prompt = open(args.prompt_file, encoding='utf-8').read().strip()
    md_path = os.path.join(work, 'answer.md')
    cmd = ['claude', '-p', prompt]
    env = {k: v for k, v in os.environ.items() if not k.startswith('CLAUDE')}
    with claude_slot():
        res = subprocess.run(cmd, cwd=args.project, capture_output=True, text=True, env=env,
                             timeout=int(os.environ.get('SHOT_TIMEOUT', 1800)))
    open(md_path, 'w', encoding='utf-8').write(res.stdout)
    if args.save_answer:
        os.makedirs(os.path.dirname(args.save_answer), exist_ok=True)
        open(args.save_answer, 'w', encoding='utf-8').write(res.stdout)
    if not res.stdout.strip():
        print('EMPTY OUTPUT', res.stderr[:500], file=sys.stderr)
        sys.exit(2)
    html_path = os.path.join(work, 'shot.html')
    chars = max(80, int((args.page_width - 40) / 8.13))
    env2 = dict(os.environ, SHOT_WIDTH_CHARS=str(chars), SHOT_PROMPT=prompt, SHOT_TITLE=args.title,
                SHOT_PATH=args.shown_path, SHOT_ELAPSED=args.elapsed, SHOT_NEXT=args.next_hint)
    subprocess.run([PY, os.path.join(HERE, 'md2tui.py'), md_path, html_path],
                   check=True, env=env2, capture_output=True)
    chrome_shot(html_path, args.out, args.page_width, args.height or estimate_height(html_path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['menu', 'answer'], required=True)
    ap.add_argument('--project', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--slash', default='')
    ap.add_argument('--prompt-file', default='')
    ap.add_argument('--title', default='flowboard-claude-skills — claude')
    ap.add_argument('--shown-path', default='~/Documents/flowboard-claude-skills')
    ap.add_argument('--elapsed', default='41s')
    ap.add_argument('--next-hint', default='請接著說明下一步')
    ap.add_argument('--rows', type=int, default=22)
    ap.add_argument('--height', type=int, default=0)
    ap.add_argument('--page-width', type=int, default=1240)
    ap.add_argument('--save-answer', default='', help='把 claude 回覆另存一份，供日後重新渲染')
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        (mode_menu if args.mode == 'menu' else mode_answer)(args, work)
    print('OK', args.out)


if __name__ == '__main__':
    main()
