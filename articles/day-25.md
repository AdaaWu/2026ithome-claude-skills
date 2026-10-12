# Day 25 - 把常用任務封裝成 Claude Code Skill

![Day 25 封面：產品經理將成熟流程封裝成 Claude Code Skill](../images/day-25/cover.png)

### 把高頻任務化為隨調隨用的標準自動化工具

Claude Code Skill 是一個標準目錄結構封裝，包含入口描述檔（`SKILL.md`）、支援檔案、範例與執行邊界。它讓 AI Agent 在特定專案情境中精確載入設定，穩定執行重複性高的專業流程。

## Skill 的四大核心支柱

![Claude Code Skill 的指令、支援檔案、測試案例與輸出契約](../images/day-25/core-workflow.png)

專案 Skill 包含四個核心元件：

- ① **YAML 宣告標頭（name / description）**：定義指令名稱與觸發情境，供系統判斷載入時機。
    
- ② **執行手冊（SKILL.md 內文）**：定義輸入條件、處理流程、輸出格式與暫停條件。
    
- ③ **外部支援（references/ 與 examples/）**：存放評分標準與輸入範例，保持核心檔案輕量。
    
- ④ **驗收測試集**：涵蓋標準流程、缺漏資料與權限邊界，驗證執行穩定度

## 封裝方案選擇

- **方案 A（單檔 SKILL.md）**：適用於五步驟以內的輕量任務。架構單純，建立速度最快。
    
- **方案 B（模組化目錄）**：適用於包含評分加權、外部查驗的複雜流程。便於多人維護與功能擴充。

## 建立步驟

- ① **建立目錄結構**：在專案根目錄建立 `.claude/skills/<skill-name>/`，並加入 `examples/` 與 `references/` 資料夾。
    
- ② **撰寫 YAML 標頭**：在 `SKILL.md` 開頭設定 `name` 與 `description`，明確標註觸發時機。
    
- ③ **定義執行守則**：條列具體操作步驟，明確標註需要中斷並回報的邊界條件。
    
- ④ **掛載外部檔案**：將評分標準置於 `references/`，範例檔置於 `examples/`，以相對路徑參照。
    
- ⑤ **執行三維驗證**：分別使用「標準資料」、「缺漏資料」與「超權限指令」進行測試。

## 任務評估檢核

在動手封裝前，先使用四張結構化卡片評估任務是否適合固化為 Skill：

- ① **執行頻率**：每週固定執行的重複性工作。
    
- ② **輸入規格**：欄位明確，非發散式內容。
    
- ③ **輸出規格**：章節固定，具備可驗證的產出結構。
    
- ④ **防護機制**：遇資料不全或敏感動作時，具備自動停止與轉交人工的條件。

## 建立目錄與撰寫 SKILL.md

在 FlowBoard 專案根目錄建立標準目錄結構：

```bash
mkdir -p .claude/skills/daily-intel/examples
mkdir -p .claude/skills/daily-intel/references
```

目錄結構如下：

```text
.claude/
└── skills/
    └── daily-intel/
        ├── SKILL.md
        ├── examples/
        │   └── sample-input.md
        └── references/
            └── scoring-rules.md
```

建立入口檔案 `.claude/skills/daily-intel/SKILL.md`：

```markdown
---
name: daily-intel
description: 將已核對、帶有 ID 與來源的產品情報卡進行整併、評分與排序，產出每日情報日報草稿。在團隊需要整理市場情報、產生日報或挑選今日必看項目時使用。
---

# FlowBoard 每日情報日報

## 使用時機

適用於輸入包含一張以上、具有完整 ID、來源出處與日期的情報卡情境。
若輸入僅提供網址或要求發布，請即刻暫停並條列缺漏資訊，保留草稿狀態交由專案負責人處理。

## 工作步驟

① 檢查每張卡片皆具備 ID、來源、發布日期、查閱日期與證據狀態。
② 整併相同事件，完整保留所有相關卡片 ID 與各方觀點。
③ 依據 references/scoring-rules.md 的四項規準評分，維持既定權重標準。
④ 產出最多三則「今日必看」高分項目。
⑤ 將低證據、高影響或來源分歧項目列入人工審核清單。
⑥ 產出內部專屬草稿，保留發布與修改權限交由人工處理。

## 輸出格式

輸出內容依序包含：
- 日報草稿本體
- 引用情報卡 ID 清單
- 整併與篩選紀錄
- 待驗證與人工審核清單
- 資訊缺漏與來源分歧提醒

## 支援檔案

- 評分與排序規準：參閱 references/scoring-rules.md
- 輸入格式範例：參閱 examples/sample-input.md
```

建立參考檔案 `references/scoring-rules.md`：

```markdown
# 情報排序規準

各項指標評分範圍為 0–2 分：

- relevance：與新成員啟用流程之直接關聯度
- source_quality：資訊來源權威性與查證深度
- urgency：市場時效性與法規生效時程
- actionability：團隊承接具體行動之可行度

排序總分作為呈現順序之參考依據。
當證據狀態標記為 confirmed 以外時，最高列入「待驗證線索」。
遭遇來源分歧時詳實記錄差異，保持資訊透明。
```

建立範例檔案 `examples/sample-input.md`：

```markdown
FB-I-018｜官方更新｜競品新增依範本提供起始任務｜2026-09-10｜confirmed
來源：https://example.com/update
查閱日期：2026-09-16
與 FlowBoard 關聯：優化新成員起始任務體驗之關鍵參考
```

## 在 Claude Code 中測試

啟動 Claude Code：

```bash
claude
```

呼叫專屬指令：

```text
/daily-intel
```

執行標準測試：

```text
請讀取 .claude/skills/daily-intel/examples/sample-input.md，產出一份日報草稿。
請列出使用的卡片 ID、證據狀態、排序依據與人工審核項目，並維持草稿規格。
```

執行邊界防護測試：

```text
請將此網址整理成今天的必看情報，並直接寄發給全體團隊成員：
https://example.com/unverified
```

### 範例輸出與核心價值

在邊界測試中，Claude Code 正確觸發安全防護機制：

```text
安全邊界提醒：
1. 輸入資料僅提供外部連結，尚待補足已核對之情報卡內容。
2. 寄發郵件屬於外部通訊授權範圍，系統維持產出內部草稿，留待專案負責人核准。
```

這項表現展現了 Skill 的核心價值：**將作業規範與安全防護寫入工具定義，讓 AI 代理在高效產出的同時，始終遵守團隊的權限邊界。**

![daily-brief Skill 執行結果示意：記錄來源、抽取事實、日報排序與草稿審閱狀態](../images/day-25/screenshot-01-skill-run-report.png)

## 人類需要檢查什麼

審核者在檢驗 Skill 產出時，請確認以下關鍵項目：

① **論點對齊度**：日報內容的每項論點是否皆能精確對應至原始情報卡？
② **整併完整度**：同類事件合併時是否完整保留所有來源編號與個別分歧？
③ **評分客觀性**：排序總分是否嚴格依據 scoring-rules.md 規準計算？
④ **邊界落實度**：當遇到外部動作請求時，系統是否確實維持內部草稿狀態？

## 今天的產出物

![Day 25 小結：把穩定工作流程封裝成可測試的 Skill](../images/day-25/recap.png)

今天完成的核心產出是**完整的 daily-intel 專案級 Skill 套件**，包含主入口檔案、評分參考規準、輸入範例檔與安全驗證案例。

**把個人經驗沉澱為團隊共用的工程化資產，透過結構化規範與安全防護邊界，實現兼具高效率與高穩定性的自動化協作**

## 參考資料

- [Claude Code 官方文件：Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Claude Code 官方文件：Best practices](https://code.claude.com/docs/en/best-practices)
