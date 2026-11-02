# SUMMARY — Gemini — 2026-11-02_delta_w01_gap12

- **App:** gemini | **Mode:** delta (visibility gap12) | **Bot:** check · collector
- **IDs (12/12):** CU10 EN03 GN05 OC01 OC09 PR05 ST09 ST13 ST19 TR10 TR04 TR08
- **Prompts file:** `inputs/run_lists/prompts_delta_2026-11-02_w01_gap12.csv`
- **Session:** signed_out_shared_profile (Incognito not confirmable in automation browser; Sign in visible throughout)
- **Model:** Flash-Lite
- **Egress:** IN / box Cloudflare (browser waves 1–3: ip `49.249.146.90`, colo DEL / Delhi; wave 4 meta used Shell cloudflare trace colo PDX IPv6 — loc=IN). User computer offline; BRIEF OK.
- **Suffix:** ` I'm shopping in the USA.`
- **Tabs:** 3 | **Overlap:** yes (4 waves of 3)
- **Started (UTC):** 2026-11-02 11:31:35
- **Finished (UTC):** 2026-11-02 11:46:55
- **Wall seconds:** 920 (~15.3 min)

## Citations / method (Sources panel DOM scrape first)
| PID | Cites | capture_quality | chat_url |
| --- | ---: | --- | --- |
| CU10 | 9 | text_reconstructed_html | https://gemini.google.com/app/7c44c249eb5ac32f |
| EN03 | 6 | text_reconstructed_html | https://gemini.google.com/app/24a7c41924c8d03e |
| GN05 | 7 | text_reconstructed_html | https://gemini.google.com/app/ec8a50accc1d1f71 |
| OC01 | 7 | dom_innerHTML | https://gemini.google.com/app/d8d031aae3ffaf8f |
| OC09 | 8 | dom_innerHTML | https://gemini.google.com/app/832961d6b9cb25ff |
| PR05 | 5 | text_reconstructed_html | https://gemini.google.com/app/b6971c9ad480059a |
| ST09 | 5 | text_reconstructed_html | https://gemini.google.com/app/0b3a2a40e79c22b0 |
| ST13 | 12 | text_reconstructed_html | https://gemini.google.com/app/b5a34c19efd8b043 |
| ST19 | 10 | text_reconstructed_html | https://gemini.google.com/app/af3f0cdb6110e682 |
| TR10 | 9 | text_reconstructed_html | https://gemini.google.com/app/0f87bdd31949dd06 |
| TR04 | 6 | text_reconstructed_html | https://gemini.google.com/app/a1ebea019967afb1 |
| TR08 | 7 | text_reconstructed_html | https://gemini.google.com/app/4776da3651903b80 |

**Total citation rows:** 91 (panel rows; duplicate text-fragment URLs kept as separate rows)

- Opened Sources via ⋮ → View sources → Sources tab; scraped `inline-source-card` rows (no chip-by-chip).
- Console / `gemini_console_paste.js` **not used** (DOM-first; Console only if DOM fails — never needed).
- Most `answer.html` / `sources_panel.html` are reconstructed from scraped text+hrefs (`text_reconstructed_html`); OC01/OC09 got `dom_innerHTML`.

## Angara mentions (answer text / citations)
- **answer text:** CU10, GN05, OC01, ST13, ST19, TR10, TR04, TR08
- **citations (panel):** CU10, OC01, ST13, ST19, TR04, TR08
- ST13 cites Forbes card with Angara snippet; ST19 has angara.com cards; TR04 has Angara rows.

## Friction / redos
- ST19: navigated away mid-stream from first chat (`63fba25af50a64ae`); signed-out chat lost; re-sent in fresh chat (`af3f0cdb6110e682`) — only second kept.
- Chrome throttled background tabs; brought to front to finish.
- Many folders: `shot_1.png` == `shot_sources.png` (panel open, answer tail visible).
- Wave 4 egress IP from Shell curl (not browser) — noted in meta.
- `captured_at_utc` approximate on later waves.

## Failures
- None. All 12 have answer.txt + citations.csv + sources_panel.html + meta + shots.

## CSVs / Drive / git
- No live_csv Build/Load.
- Local path: `runs/2026-11-02_delta_w01_gap12/raw/gemini/` (+ this SUMMARY + `run_info_gemini.json`).
- Push to `Ai_visibility_source` per BRIEF — see ping / follow-up.
