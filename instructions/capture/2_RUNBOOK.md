# Capture Runbook

capture/2_RUNBOOK v2.1 · 2026-10-27

Policy for the **Capture** task: what needs approval, how sessions and egress work, how bots share work, and what to do when something fails. The order of work is in `1_CHECKLIST.md`. What to click and save in each app is in `3_APP_GUIDE.md`. Names are defined in `README.md`.

**Add prompts** task: read only the "Prompts" section.

---

## 1. Approvals

| Needs the human's explicit yes | Does not need approval |
|---|---|
| Any run starting (with apps + IDs given) | Using the signed-out shared profile instead of Incognito |
| A full run (all `active=1` rows) | Re-running a contaminated ID in the same run |
| Proceeding with non-US egress (tag `IN`) | Opening a fresh Incognito window or new chat |
| Adding prompts to `inputs/` | Writing your own app's raw folders and run files |
| Any change to folder structure, names or file formats | |
| Unpausing the Claude "Resume" routine (stays paused) | |

---

## 2. Runs

| Mode | Scope |
|---|---|
| **Full** | Every row with `active=1` in `prompts_v3_final.csv` |
| **Delta** | Only the IDs the human listed, or rows in a `prompts_delta_*.csv` the human supplied |

- One `run_id` per run. All bots in that run use it. Example: `2026-10-27_delta_v3`.
- `prompt_id` stays the prompt id only; bot name goes in `meta.captured_by` / `source`, not in ids.
- Prompts added later are a new **delta** run with a new `run_id`. Never add captures to an older run folder.
- One source per run: `grok_bot_ui` (normal), `parallel_test`, `schedule` or `api`. Test or experimental captures get their own `run_id` with a note that says so (for example `2026-10-28_delta_paralleltest`).

---

## 3. Prompts

**Where prompts come from (nowhere else):**
1. `inputs/prompts_v3_final.csv`, rows with `active=1`
2. `inputs/prompts_delta_*.csv` that the human supplied
3. Exact prompt text the human pasted in the chat

Never invent a `prompt_id`, `prompt_text` or `followup_text`. If the human asks for "N new prompts" without giving them, ask for the rows.

**USA suffix:** scored runs always use the suffix (send rule in the Checklist). Runs without the suffix are research only. They skew heavily toward India results, so they need their own `run_id` with `nosuffix` in the note and a line in SUMMARY.

**Adding prompts (Add prompts task):**
1. Get the exact rows from the human.
2. Check each new `prompt_id` doesn't already exist in `prompts_v3_final.csv` or any delta file.
3. Write them to a new file `inputs/prompts_delta_YYYY-MM-DD.csv` with the same columns as the master:
   `prompt_id,old_id,category,scored_on,status,prompt_text,followup_text,active`
4. Show the rows to the human and get a yes before uploading.
5. Never rewrite `prompts_v3_final.csv`. If the human asks to merge deltas into the master: download it, append the rows, confirm the new row count = old count + added rows, upload as a new file, move the old file to `archive/`.

---

## 4. Sessions

| App | Sign-in | Chat mode | New chat | `meta.session` value |
|---|---|---|---|---|
| ChatGPT | Signed out | Chrome Incognito **or** signed-out shared profile | Every prompt | `incognito` or `signed_out_shared_profile` |
| Gemini | Signed out | Chrome Incognito **or** signed-out shared profile | Every prompt | `incognito` or `signed_out_shared_profile` |
| Claude | Signed in (set by the human) | Claude's own **Incognito chat toggle** on | Every prompt | `claude_incognito_chat` |

- **Turn 2** of a multi-turn prompt always goes in the **same chat** as turn 1.
- **Never ask for, store or type credentials.** The human sets sign-in state.
- **ChatGPT / Gemini must be signed out.** Signed-in accounts change answers and citations.
- **Claude must use the Incognito chat toggle.** Normal signed-in chats carry over account history and skew answers. A Chrome Incognito window does not replace the toggle.
- **Claude Free** allows about 30 messages per window. The Incognito toggle doesn't change that. Plan the ID list around the limit.
- **Record the session you actually used.** Never write `incognito` when it was the shared profile.

---

## 5. Egress

The shared box is in **Jaipur, India**, so by default every app sees Indian traffic.

1. **Check the IP inside the capture browser** (for example open ipinfo.io in the same window). A check from the shell doesn't count, because the browser may route differently.
2. Record `ip`, `egress_city` and `egress_country` in every `meta.json` and in `run_info_<app>.json`.
3. **If the country is not US**, ask the human before the first prompt:
   - (a) the human turns on Route traffic / VPN, then you check again; or
   - (b) proceed and tag `egress_country=IN`.
4. **Mid-run changes:**
   - If the human already approved IN and a "computer offline" notice appears (egress falls back to the box), **keep going**. Record the actual IP.
   - If the human has not approved IN and the IP turns non-US, **stop and ask**.
5. The box clock may show another timezone (for example America/St_Barthelemy). **Timezone is not location.** Only the browser IP check counts. The currency shown in answers (`currency_seen`) is a useful second signal.

---

## 6. Parallel bots

- **Default: one bot per app**, all on the same `run_id`.
- **Max 3 tabs per bot desktop.** Type and send in one tab at a time, because keystrokes can land in the wrong tab. Generation can finish in parallel.
- **Splitting one app across two bots:** give the helper bot a fixed ID list, the exact send texts, the `run_id` and the raw path. The helper writes only its own raw folders and reports its IDs, failures and notes back. The lead bot for that app writes `SUMMARY_<app>.md` and `run_info_<app>.json` once, after the helper reports.
- **Never ask another bot to invent prompts.**
- **If a bot thrashes** (freezes, types into the wrong tab, opens the wrong chat): stop that bot's remaining IDs, then re-run every affected ID cleanly.

---

## 7. Failures

| What happens | What to do |
|---|---|
| **ChatGPT silent send-fail**: prompt typed and sent, but the composer clears, the URL stays on chatgpt.com and no chat is created | **Stop ChatGPT at once.** Don't send the remaining IDs. Leave no empty raw folder for the failed ID. Record failed IDs with reason `silent_send_fail`. Recovery, in order: (1) open a fresh Incognito window or clear site data, (2) ask the human about Route traffic, (3) retry only the failed IDs. |
| **Contaminated answer**: sent into the wrong chat or tab, or a follow-up landed in an old chat | Rename that raw folder to `<raw folder name>__discarded_1` (`_2` for a second discard). Don't change its contents. Re-run the ID in a fresh chat into the normal folder name. List it under "Discarded" in SUMMARY. |
| **Invalid first answer** (capture error) | Same as contaminated: discard by renaming, re-run, record the redo in SUMMARY. |
| **Answer never finishes** (stalled 5+ minutes) | Save what is visible with `capture_quality=partial`, then retry once in a new chat (discard the first by renaming). If it stalls again, record the ID as failed with reason `stalled`. |
| **Claude shows a clarifying widget** instead of an answer | Capture what is visible with `capture_quality=partial`. Don't answer the widget unless the human asked you to. Note it in SUMMARY. |
| **Claude message limit reached** | Stop. List remaining IDs and when the limit resets. Never switch accounts. |
| **Captcha or bot check** you can't pass | Stop that app and ask the human. Set `bot_check=true` on any capture where it appeared. |
| **Browser freezes or you lose track of tabs** | Stop. Close the affected tabs. Re-run every ID you can't confirm was clean. |

Renaming a folder to `__discarded_N` is the **only** change allowed to a raw folder after writing. The CSV build skips any folder whose name contains `__discarded`.

---

## 8. Drive

- **Done means on Drive.** Local files alone are not done.
- Upload only under `runs/<run_id>/`. Never write to `inputs/` (except approved prompt files), `instructions/` or `live_csv/`.
- **Raw upload rule (required):** upload every raw folder **expanded** to `runs/<run_id>/raw/<app>/<raw folder>/`, one Drive folder per raw folder with its files inside (same layout as Claude). This includes `__discarded_N` folders.
- **Optional backup:** one `raw_<app>.tar.gz` per app at `runs/<run_id>/` root. It is a backup only.
- **Not allowed as the only upload:** an empty or archive-only `raw/<app>/`. A tar alone is **not done**.
- If your tool can only upload archives or single files, upload file by file into created folders (create folder, then upload each file) before reporting done. Never report done with archives only.
- **HTML over about 1 MB:** store as `answer.html.gz` (gzip of the exact bytes), keep the uncompressed copy locally, and note it in SUMMARY.
- **Before writing a file:** list its parent folder first. Never write to a file whose `trashed` flag is true. When unsure, upload a new file rather than replacing one.
- **Write one raw folder at a time.** Never run loops that write across many folders at once.

---

## 9. Timing reference

Approximate, from runs on the Jaipur box. Use it to plan, not as a target.

| App and setup | Observed | Date |
|---|---|---|
| ChatGPT, 3 tabs, 10 prompts | ~10 min (when no send-fails) | 2026-10-27 |
| ChatGPT, 3 tabs, 10 prompts | ~4 min | 2026-10-25 |
| Gemini, 3 tabs, 10 prompts | ~15 min | 2026-10-25 |
| Gemini, dual-bot Incognito, 9 prompts | ~6.5–7 min | 2026-10-26 |
| Claude Free, 1 tab sequential, 11 prompts | ~36 min | 2026-10-26 |

Claude Free usually decides total run time. Use 3 tabs when the message limit allows.
