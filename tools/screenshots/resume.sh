#!/bin/bash
# 重開機後跑這支就好：收集剩餘回覆 → 渲染成圖 → 回報缺口
# 用法：~/Documents/2026ithome-claude-skills/tools/screenshots/resume.sh
set -u
S=/private/tmp/claude-501/-Users-sunnywu-Documents-2026ithome-claude-skills/0a7d734a-4480-4c17-89ae-32facc6431aa/scratchpad
R=/Users/sunnywu/Documents/2026ithome-claude-skills
D=~/Documents/ithome-demo
export SHOT_VENV=$S/venv SHOT_SLOTS=1 SHOT_TIMEOUT=3600
mkdir -p $S/answers

# day:專案:檔名:耗時字樣:後續提問
JOBS=(
"23:chain-e1:daily-intel-output-and-review:45s:請說明待審項目的判斷依據"
"24:chain-e2:eval-diff-review:50s:請說明這次修改會影響哪些測試案例"
"25:chain-e2:daily-intel-draft-with-ids:61s:請說明排序理由用了哪些欄位"
"29:chain-f:traceability-broken-id:54s:請說明那個斷掉的 ID 該連回哪裡"
"30:chain-f:workflow-retro-unknown:66s:請說明未記錄的基準要怎麼補"
"21:chain-e1:intel-scan-evidence-status:52s:請說明哪幾張卡需要人工覆核"
"15:chain-d1:demo-spec-states-and-boundary:47s:請補上錯誤狀態的測試資料"
"16:chain-d1:user-flow-missing-exit:55s:請補上缺少去向的那個節點"
"19:chain-d2:anomaly-check-formula-and-denominator:49s:請說明第二個異常的替代解釋"
"20:chain-d2:decision-brief-with-denominator:57s:請補上每個發現的分母來源"
)

for job in "${JOBS[@]}"; do
  IFS=: read -r day proj kebab el hint <<< "$job"
  out=$R/images/day-$day/screenshot-01-$kebab.png
  [ -f "$out" ] && { echo "SKIP day-$day（圖已存在）"; continue; }
  echo "=== day-$day start $(date +%H:%M:%S) ==="
  python3 $R/tools/screenshots/shoot.py --mode answer \
    --project $D/$proj/flowboard-claude-skills \
    --prompt-file $S/prompts/day-$day-a.txt \
    --save-answer $S/answers/day-$day.md \
    --out "$out" --elapsed "$el" --next-hint "$hint" \
    && echo "=== day-$day OK $(date +%H:%M:%S) ===" || echo "=== day-$day FAIL ==="
done

echo "=== 全部結束，執行檢查 ==="
python3 $R/tools/screenshots/check_shots.py | tail -25
