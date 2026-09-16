#!/bin/bash
# 用 OpenAI gpt-image-1 生成當天的三張插圖
# 用法：./tools/gen_images.sh 14
# 需要環境變數 OPENAI_API_KEY

set -e
DAY=$(printf "%02d" "$1")
DIR="images/day-$DAY"
PROMPTS="$DIR/PROMPTS.md"

[ -z "$OPENAI_API_KEY" ] && { echo "請先設定 OPENAI_API_KEY"; exit 1; }
[ -f "$PROMPTS" ] || { echo "找不到 $PROMPTS"; exit 1; }

STYLE=$(sed -n '/^## 角色設定/,/^## 文字規則/p' images/STYLE-GUIDE.md)

gen() {
  local name="$1" section="$2"
  local body
  body=$(awk "/^## $section/,/^---$/" "$PROMPTS" | sed -n '/```text/,/```/p' | sed '1d;$d')
  echo "生成 $name ..."
  jq -n --arg p "$STYLE

$body" '{model:"gpt-image-1",prompt:$p,size:"1536x1024",quality:"high",n:1}' \
  | curl -s https://api.openai.com/v1/images/generations \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -H "Content-Type: application/json" -d @- \
  | jq -r '.data[0].b64_json // (.error.message|halt_error(1))' \
  | base64 -d > "$DIR/$name.png"
  echo "已存 $DIR/$name.png"
}

gen cover "① cover.png"
gen core-workflow "② core-workflow.png"
gen recap "③ recap.png"
echo "完成，請檢查 $DIR"
