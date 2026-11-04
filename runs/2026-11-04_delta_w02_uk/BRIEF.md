# Run 2026-11-04_delta_w02_uk — full 127-prompt UK delta

Branch: **Ai_visibility_source** (mukulsharma-spec/AI_Visibilty) — push direct, no PR (GitHub access may be pending; keep raw on box until granted).
Run list: `inputs/run_lists/prompts_delta_2026-11-04_w02_uk.csv` (= `run_list.csv`, column `send_text` is the exact send). Tick list: `ASSIGNMENT.md`.
Scope: **all 127 active prompts × 3 apps** (claude, chatgpt, gemini), r1.
Send: exact `prompt_text` + ` I'm shopping in the UK.` (space before I'm).
Multi-turn MT01–MT06: suffix on **first message only** (t1); `followup_text` sent **verbatim, no suffix**, in the same chat as t2.
**3 tabs per bot**, waves of 3, reuse same tabs (Claude: close/reopen Incognito between waves, do not refresh).

## Egress (mandatory)
User's machine with **Route traffic through this computer** ON + VPN set to **UK**. Keep Grok Bot app open, Mac awake.
Before the first prompt, verify public IP in the capture browser (e.g. ipinfo.io) shows GB; record IP/city. If routing drops (box falls back to Cloudflare/IN), stop and re-verify.
meta: `egress_country: "GB"` (ISO-2, matching prior runs' IN/US), `egress_city`, `egress_ip`.

## Folder layout
`raw/<app>/<app>__<PID>__r1__t1/{answer.html, answer.txt, meta.json, shot_*.png}`
MT followup: separate folder `raw/<app>/<app>__MTxx__r1__t2/` (same convention as 2026-10-27_delta_br20).
+ `sources_panel.html`, `citations.csv` (prompt_id,app,source_name,domain,url,source_file)
Run-level: `SUMMARY_<app>.md`, `run_info_<app>.json`, started/finished timestamps.

## Capture rules (Sources — mandatory, same as gap12)
- **Claude** (signed-in, **Incognito chat control** not plain New chat): paste don't type. After answer: click **Searched the web** → nested row toggle → scrape full title+domain+URL. Console optional: `tools/claude_console_paste.js` (set PID) after expand.
- **ChatGPT** (signed out / Incognito): Website card hrefs + chips for URLs. Console: `chatgpt_console_paste.js`.
- **Gemini** (signed out Incognito): open **Sources panel** from action bar under finished reply (⋮ / View sources) — scrape panel rows; do not click every inline chip. Console: `gemini_console_paste.js` with Sources open.
- **Every answer:** `chat_url` + full-answer screenshot. **Claude must save chat_url** (missing in gap12).
- meta: `web_search`, `session`, `egress_country`, `egress_city`, `model_ui`, `capture_quality`, `chat_url`.
- Strip source-chip labels from `answer.txt` where possible.
- Do **not** Load `live_csv`. Push raw to `Ai_visibility_source` when your app's 127 (+6 t2) are done; Grok Bot coordinates Build.

## Assignment
- **Grok Bot** → Claude Incognito, 3 tabs, all 127
- **Friday** → ChatGPT signed-out/Incognito, 3 tabs, all 127
- **check · collector** → Gemini Incognito, 3 tabs, all 127

Done = 133 folders per app (127 t1 + 6 MT t2) with answer + chat_url + screenshot + citations when search UI present + SUMMARY.
