# Run 2026-11-02_delta_w01_gap12 — 12-prompt visibility gap delta

Branch: **Ai_visibility_source** (mukulsharma-spec/AI_Visibilty) — push direct, no PR.
Run list: `inputs/run_lists/prompts_delta_2026-11-02_w01_gap12.csv`
IDs (all 3 apps × 12): CU10 EN03 GN05 OC01 OC09 PR05 ST09 ST13 ST19 TR10 TR04 TR08
Send: exact `prompt_text` + ` I'm shopping in the USA.` | **box Cloudflare egress** (user computer offline; note in meta) | r1 t1
**3 tabs per bot**, waves of 3, reuse same tabs (Claude: close/reopen Incognito between waves, do not refresh).

## Folder layout
`raw/<app>/<app>__<PID>__r1__t1/{answer.html, answer.txt, meta.json, shot_*.png}`
+ `sources_panel.html`, `citations.csv` (prompt_id,app,source_name,domain,url,source_file)
Run-level: `SUMMARY_<app>.md`, `run_info_<app>.json`, started/finished timestamps.

## Capture rules (Sources — mandatory)
- **Claude** (signed-in, **Incognito chat control** not plain New chat): paste don't type. After answer: click **Searched the web** → nested row toggle → scrape full title+domain+URL. Console optional: `/workspace/ai-visibility/tools/claude_console_paste.js` (set PID) after expand.
- **ChatGPT** (signed out / Incognito): Website card hrefs + chips for URLs. Console: `chatgpt_console_paste.js`.
- **Gemini** (signed out Incognito): open **Sources panel** from action bar under finished reply (⋮ / View sources) — scrape panel rows; do **not** click every inline chip. Console: `gemini_console_paste.js` with Sources open.
- meta: `web_search` true/false, `session`, `egress_country` (note box/Cloudflare if applicable), `capture_quality`.
- Do **not** Load `live_csv`. Push raw to `Ai_visibility_source` when your app's 12 are done; Grok Bot coordinates Build.

## Assignment
- **Friday** → ChatGPT all 12
- **check · collector** → Gemini all 12
- **Grok Bot** → Claude all 12

Done = 12 folders with answer + citations when search UI present + SUMMARY.
