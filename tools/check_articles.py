from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
problems = []
for day in range(1, 31):
    path = root / "articles" / f"day-{day:02}.md"
    if not path.exists():
        problems.append(f"missing: {path.name}")
        continue
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    expected = rf"^# Day {day}｜"
    if not lines or not re.match(expected, lines[0]):
        problems.append(f"bad title: {path.name}")
    chars = len(re.sub(r"\s+", "", text))
    if chars < 1800:
        problems.append(f"short ({chars} chars): {path.name}")
    for required in ("今天", "產出物"):
        if required not in text:
            problems.append(f"missing '{required}': {path.name}")
    if "FlowBoard" not in text:
        problems.append(f"missing case: {path.name}")
    # Day 29 is an internal synthesis whose evidence is the preceding articles.
    if day != 29 and "參考資料" not in text:
        problems.append(f"missing references: {path.name}")

if problems:
    print("\n".join(problems))
    raise SystemExit(1)
print("30 articles passed structural checks")
