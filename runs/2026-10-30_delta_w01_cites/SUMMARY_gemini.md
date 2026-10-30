# SUMMARY_gemini — 2026-10-30_delta_w01_cites

## 1. Run
- **run_id:** `2026-10-30_delta_w01_cites`
- **app:** gemini
- **mode:** delta
- **bot(s):** check · collector
- **started_at_utc:** 2026-10-30 11:33:07
- **ended_at_utc:** 2026-10-30 11:49:35
- **prompts_file:** `inputs/run_lists/prompts_delta_2026-10-30_w01_cites.csv` (IDs also confirmed in `inputs/prompts_v3_final.csv`)
- **guide_version:** capture/3_APP_GUIDE v2.3.2 + BRIEF Sources-panel rule

## 2. Captured
- GN05, EN03, ST09, TR10, OC01 (all r1/t1, USA suffix)

## 3. Failed
- none

## 4. Discarded and re-run
- OC01: first submit duplicated into chat `49cd04a008d52189` — abandoned; re-ran once in fresh chat `337245ca41c1105e` (files are from the fresh chat only; no `__discarded` folder kept)

## 5. Session and egress
- **session:** `signed_out_shared_profile` (Sign in visible)
- **egress:** ip `49.249.146.90`, Dadri (Uttar Pradesh), IN — IN approved (task brief)
- **model_ui:** Flash-Lite
- **tabs:** sequential (1 prompt at a time) for Sources-panel scrape

## 6. Quality caveats
- **Sources panel required:** each ID has `citations.csv` with `source_file=html_sources_panel` (name + domain + full href). EN03/ST09/TR10/OC01 also have `sources_panel.html` + `shot_sources.png`.
- **GN05:** `citations.csv` complete (7 rows) but `sources_panel.html` missing; `answer.html` is `text_wrapped_html` reconstructed from innerText (sandbox could not write raw DOM on first attempt). Later IDs used DevTools Blob download for raw `message-content` outerHTML.
- Citation counts: GN05=7, EN03=4, ST09=3, TR10=7, OC01=4
- ST09 Angara href uses `/in-en/` path (IN egress). OC01/ST09 currency_seen USD from Sources snippets.
- shot_1 viewport; DevTools closed after each Blob download (except TR10 shot_sources briefly shows DevTools).

## 7. Repo path
- `runs/2026-10-30_delta_w01_cites/` and `runs/2026-10-30_delta_w01_cites/raw/gemini/` on branch `Ai_visibility_source` (expanded raw folders; no Drive; no CSVs built)
