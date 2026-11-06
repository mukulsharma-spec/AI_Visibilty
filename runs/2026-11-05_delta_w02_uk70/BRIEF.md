# Run 2026-11-05_delta_w02_uk70 — 70-prompt UK VPN delta

Branch: **Ai_visibility_source** (`mukulsharma-spec/AI_Visibilty`) — push raw (+ Build csv when ready) to this branch; **do not Load live_csv** until human yes.
Run list: `inputs/run_lists/prompts_uk_vpn70_2026-11.csv` (also `run_list.csv` here). **70 prompts**, active=1.
Scope: **70 × 3 apps** (claude, chatgpt, gemini), r1. Multi-turn: MT02, MT03, MT06 → extra t2 folders (73 folders/app).

## Send
- Turn 1: exact `prompt_text` **as written in the CSV — NO shopping suffix** (user 2026-11-05).
- Turn 2 (MT only): `followup_text` verbatim, **no suffix**, same chat.
- **3 tabs per bot**, waves of 3; reuse tabs. Claude: Incognito chat toggle; close/reopen Incognito between waves (don't refresh).

## Egress
Route traffic + UK VPN. Browser IP should be **GB**. Tag meta `egress_country: "GB"`, city, IP.
Browser check earlier today: 206.189.112.208 London GB (DigitalOcean) — re-verify before first send if unsure.

## Layout
`raw/<app>/<app>__<PID>__r1__t1/{answer.html,answer.txt,meta.json,shot_*.png}`
MT t2: `raw/<app>/<app>__MTxx__r1__t2/`
Also `sources_panel.html` / citations when search UI present. Run-level: `SUMMARY_<app>.md`, `run_info_<app>.json`.

## Capture (Sources mandatory)
- **Claude** (signed-in, Claude Incognito Chat): paste; scrape Searched the web panel.
- **ChatGPT** (signed out / Incognito): chips + Sources.
- **Gemini** (signed out Incognito): Sources panel.
- Every answer: `chat_url`, screenshot, `capture_quality`, `model_ui`.

## Assignment
- **Grok Bot** → Claude, all 70 (+3 t2)
- **Friday** → ChatGPT, all 70 (+3 t2)
- **check · collector** → Gemini, all 70 (+3 t2)

Done = 73 folders/app with answer + chat_url + shot + cites when present + SUMMARY. Then Grok Bot Build+push to Ai_visibility_source.
