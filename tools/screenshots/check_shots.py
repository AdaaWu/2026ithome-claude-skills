#!/usr/bin/env python3
"""覆核每日截圖與文章插入狀態。"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BAD_WORDS = ['Claude Team', 'Claude Max', 'Claude Pro', 'sunny.wu@', 'stockfeel',
             'ithome-demo', 'chain-a', 'chain-b', 'chain-c', 'chain-d', 'chain-e', 'chain-f']


def png_size(path):
    out = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', path],
                         capture_output=True, text=True).stdout
    w = re.search(r'pixelWidth: (\d+)', out)
    h = re.search(r'pixelHeight: (\d+)', out)
    return (int(w.group(1)), int(h.group(1))) if w and h else (0, 0)


def main():
    problems = []
    for day in range(2, 31):
        dd = f'{day:02d}'
        img_dir = os.path.join(ROOT, 'images', f'day-{dd}')
        art = os.path.join(ROOT, 'articles', f'day-{dd}.md')
        shots = sorted(f for f in os.listdir(img_dir) if f.startswith('screenshot-')) \
            if os.path.isdir(img_dir) else []
        text = open(art, encoding='utf-8').read() if os.path.exists(art) else ''
        linked = re.findall(r'!\[[^\]]*\]\(\.\./images/day-%s/(screenshot-[^)]+)\)' % dd, text)

        if not shots:
            problems.append(f'day-{dd}: 沒有截圖')
            continue
        for s in shots:
            path = os.path.join(img_dir, s)
            w, h = png_size(path)
            if h > 4200:
                problems.append(f'day-{dd}/{s}: 過高 {h}px，建議拆圖')
            if w == 0:
                problems.append(f'day-{dd}/{s}: 讀不到尺寸，檔案可能壞了')
            if s not in linked:
                problems.append(f'day-{dd}/{s}: 圖已產出但文章沒引用')
        for l in linked:
            if l not in shots:
                problems.append(f'day-{dd}: 文章引用了不存在的 {l}')
        for bad in BAD_WORDS:
            if bad in text:
                problems.append(f'day-{dd}.md: 內文出現不該有的字串「{bad}」')
        print(f'day-{dd}: 圖 {len(shots)} 張，文章引用 {len(linked)} 張')

    print('\n=== 問題清單 ===')
    print('\n'.join(problems) if problems else '無')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
