import os, pty, sys, time, select, fcntl, termios, struct, json
import pyte

COLS = int(os.environ.get('SHOT_COLS', 100))
ROWS = int(os.environ.get('SHOT_ROWS', 34))

def spawn(cmd, cwd):
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(cwd)
        env = {k: v for k, v in os.environ.items() if not k.startswith('CLAUDE')}
        env['TERM'] = 'xterm-256color'
        env['COLUMNS'] = str(COLS); env['LINES'] = str(ROWS)
        os.execvpe(cmd[0], cmd, env)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack('HHHH', ROWS, COLS, 0, 0))
    return pid, fd

def pump(fd, stream, seconds):
    end = time.time() + seconds
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try:
                data = os.read(fd, 65536)
            except OSError:
                return
            if not data:
                return
            stream.feed(data.decode('utf-8', 'replace'))

def dump(screen, path):
    out = []
    for y in range(screen.lines):
        row = []
        for x in range(screen.columns):
            ch = screen.buffer[y][x]
            row.append({'c': ch.data, 'fg': ch.fg, 'bg': ch.bg, 'b': ch.bold, 'i': ch.italics, 'u': ch.underscore, 'r': ch.reverse})
        out.append(row)
    with open(path, 'w') as f:
        json.dump({'rows': screen.lines, 'cols': screen.columns, 'cells': out}, f)

if __name__ == '__main__':
    cwd = sys.argv[1]
    steps = json.load(open(sys.argv[2]))
    screen = pyte.Screen(COLS, ROWS)
    stream = pyte.ByteStream(screen) if False else pyte.Stream(screen)
    pid, fd = spawn(['/bin/zsh', '-f'], cwd)
    pump(fd, stream, 1.0)
    os.write(fd, b"export PS1='%~ %# '; clear\n")
    pump(fd, stream, 1.0)
    screen.reset()
    for st in steps:
        if 'wait' in st:
            pump(fd, stream, st['wait'])
        if 'send' in st:
            os.write(fd, st['send'].encode())
        if 'snap' in st:
            dump(screen, st['snap'])
            print('snap ->', st['snap'], flush=True)
    os.write(fd, b'\x03')
    time.sleep(0.3)
    try:
        os.kill(pid, 9)
    except Exception:
        pass
