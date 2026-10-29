# Changelog

Record of rule and structure changes, newest first. Bots read this only for the **Edit instructions** task. When you change any instruction file: bump its version line, then add an entry here saying what changed and why.

---

## v2.3 · 2026-10-29: `Ai_visibility_source` is the working branch

### Branch workflow
- **`Ai_visibility_source` is now the sole working source of truth.** All assistants read from and commit/push directly to this branch.
- No PR into `main` is required for day-to-day capture, CSV build, load, or run hand-off unless a human explicitly asks.
- `main` may lag behind `Ai_visibility_source`; do not treat `main` as authoritative for ops.
- Branch created from `cursor/add-delta-w01-new-run-620d`.

### Updated files
- `README.md` v2.3: source-of-truth statement and rule 6 now specify `Ai_visibility_source`
- `capture/1_CHECKLIST.md` v2.3: section D specifies push to `Ai_visibility_source`
- `capture/2_RUNBOOK.md` v2.3: section 8 specifies commit/push to `Ai_visibility_source`, no PR
- `csv/1_BUILD_AND_LOAD.md` v2.3: Load section specifies commit/push to `Ai_visibility_source`, no PR

### What stays the same
- Weekly `run_id` naming convention (wNN, wNN_new, etc.)
- SCHEMA v2.2 (30-column answers.csv with split rank fields)
- All approval rules, pipeline stages, folder structures

---

## v2.2 · 2026-10-29: schema rank field split and inputs restructure

### Schema Changes
- **BREAKING**: Split `ai_angara_rank_of_n` (string) into two separate fields:
  - `ai_angara_rank` (int or blank): 1-based rank position
  - `ai_angara_rank_n` (int or blank): Total number of rank slots (was "of N")
- Column count in `answers.csv` increased from 29 to 30
- Enables numeric sorting/filtering on rank data

### Repository Structure
- Master prompt and brand alias files remain at `inputs/` root:
  - `inputs/prompts_v3_final.csv`
  - `inputs/brand_aliases_v3.csv`
- One-off/delta run lists moved to `inputs/run_lists/`:
  - `prompts_delta_2026-10-27.csv`
  - `prompts_delta_2026-10-27_br20.csv`
  - `prompts_nosuffix_2026-10-28_12.csv`

### Weekly run_id Convention
- Added naming convention `YYYY-MM-DD_<type>_<label>` with labels: wNN (weekly core), wNN_new (new prompts), wNN_fix (re-capture), nosuffix (test), usegress (US-egress test)
- Week 1 = existing baseline + Oct 27 deltas (`2026-10-baseline_v3`, `2026-10-27_delta_v3`, `2026-10-27_delta_br20`)
- Test runs (nosuffix) never scored in main trends; usegress gets separate trend line
- Grok Bot proposes run_id; human confirms before capture

### Documentation
- Updated `csv/2_SCHEMA.md` to v2.2 with new rank fields
- Added run_id naming section to README.md

### GitHub-only hand-off (2026-10-29)
- **Source of truth and "done" = this GitHub repo, branch `Ai_visibility_source`.** Removed external shared-folder requirement from all ops wording.
- Capture checklist, runbook, app guide, build/load docs, and README now say commit/push under `runs/<run_id>/`, `inputs/`, `live_csv/`, `instructions/` on `Ai_visibility_source`.
- Parallel-bot handoff: bots write into the shared working directory and push to `Ai_visibility_source` (coordinate to avoid conflicts).
- Pipeline stages (capture → build → load) and approval rules unchanged; only storage/hand-off surface changed.
- Added Git LFS guidance note for large screenshots if repository binary size grows past a few hundred MB.

### Migration Notes
- `live_csv/` may remain on v2.1 until data migration is completed
- No automated data migration is performed; coordinate with data team if needed
- Check column count to distinguish v2.1 (29) from v2.2 (30)

---

## v2.1 clarification · 2026-10-27: raw upload rule (not a version bump)

### What changed
- `capture/2_RUNBOOK.md` §8, `capture/1_CHECKLIST.md` D, `capture/3_APP_GUIDE.md` SUMMARY, README rule 6: raw folders **must** be uploaded expanded to `runs/<run_id>/raw/<app>/<raw folder>/` (same layout as Claude). `raw_<app>.tar.gz` at run root is an optional backup only. Empty or archive-only `raw/<app>/` is not done.
- Checklist adds a folder-count check.

### Why
- Run `2026-10-27_delta_br20`: ChatGPT and Gemini were uploaded as tars only, leaving `raw/<app>/` unusable for review; fixed by uploading the expanded folders (ChatGPT 22 folders / 88 files, Gemini 23 folders / 112 files).

---

## v2.1 · 2026-10-27: layout + schema lock + live_csv migration + instruction sync

### What changed
- Moved instruction files into `instructions/capture/` and `instructions/csv/` so paths match README.
- Created root `archive/` and `reports/` folders.
- Locked allowed `ai_answer_format` values (22) into `csv/2_SCHEMA.md` section 2a.
- Documented `signed_in` as lowercase `true`/`false` (v1 files used `True`/`False`).
- Clarified `prompt_id` is only the prompt id; date/batch in `run_id`.
- Migrated `live_csv/` to SCHEMA v2 columns with **split** `run_id`:
  - `2026-10-baseline_v3` = 321 answers (2026-10-22/23)
  - `2026-10-27_delta_v3` = 18 answers (delta prompts)
- Row counts unchanged: answers 339, brand_mentions 2045, citations 1347 (0 exact duplicates).
- Backed up pre-migration CSVs to `archive/live_csv_backup_2026-10-27/`.
- Moved `*_facts.csv` to `archive/live_csv_facts_only_v1/`.
- Synced remaining instruction text (README, Build/Load, Checklist, Runbook, App Guide) to v2.1: `prompt_id` vs `run_id`, lowercase `signed_in` in CSVs, locked `ai_answer_format` §2a, live_csv migration complete, example `run_id`s use `2026-10-27_delta_v3`.

### Open items
- [x] Confirm how `signed_in` is written → lowercase `true`/`false` after migration.
- [x] List `ai_answer_format` values → locked in SCHEMA 2a.
- [x] Confirm role of "check · collector" → third collector (already in README).
- [ ] Verify robots.txt / CDN access for AI bots (from study notes; not a pipeline task).

---

## v2 · 2026-10-27: instruction restructure

### What changed

| Area | Before (v1) | Now (v2) |
|---|---|---|
| Entry point | README described folders; bots read every file | `README.md` routes each task to only the files it needs |
| Instruction files | 6 flat files with overlapping rules | `capture/` (3 files) and `csv/` (2 files); each rule lives in one file |
| `run_key` | Capture: `app\|id\|r1\|1\|date`; CSV: `app\|id\|r1\|t1` | One format everywhere: `app\|id\|r1\|t1`; the date lives in `run_id` |
| Raw folder names | Contained `\|` | `__` instead (`claude__CH03__r1__t1`) |
| Raw path | Three different versions | `runs/<run_id>/raw/<app>/<raw folder>/` |
| Run files | One `SUMMARY` + `run_info.json` per run | One per app: `SUMMARY_<app>.md`, `run_info_<app>.json` (parallel bots never overwrite) |
| Screenshots | `.webp` in spec, `.png` in guide | `.png` |
| ChatGPT / Gemini session | Incognito required; shared profile needed approval | Signed out is what matters; Incognito or shared profile, no approval; record which |
| Bad captures | "Discard" (conflicted with "never delete raw") | Rename folder to `__discarded_N`; contents untouched; CSV build skips it |
| `meta.json` | No `run_id`, `prompt_sent`, `captured_by` | All three added |
| CSV flow | Parse → facts, Label → labels, Merge → merged, Load | **Build CSVs** straight from raw into the 3 dashboard files, then **Load** |
| CSV schema | v1: 25 / 19 / 10 columns, no run identifier | v2: 29 / 20 / 11 columns; `run_id` first; `session`, `egress_country`, `source` added; fixed column order |
| `live_csv/` | Merged files + facts-only duplicates | Only `answers.csv`, `brand_mentions.csv`, `citations.csv` |
| Brand list | Appendix inside the pipeline spec | `inputs/brand_aliases_v3.csv` (same 62 patterns, unchanged) |
| Flowchart | Separate file, partly out of date | Folded into `csv/1_BUILD_AND_LOAD.md` and README pipeline table |
| Incident rules | Runbook §11–13, by date | Moved into their topics; history kept below |

### Decisions made in v2

- Duplicate links within one answer are kept once in `citations.csv`.
- App links (chatgpt.com, claude.ai, gemini.google.com, Google account/support pages) are dropped from citations.
- Gemini citation chips without links become rows with blank `url` and `source_file=html_chip`.
- `web_search_marker` comes from `meta.web_search`; old per-app text rules apply only to older runs.
- A stalled answer (5+ minutes) is saved as `partial`, retried once, then marked failed with reason `stalled`.
- Runs without the USA suffix need `nosuffix` in their `run_id` and are never scored.
- Prompt additions go into new `prompts_delta_YYYY-MM-DD.csv` files; the master is merged only on request.
- Loading backs up `live_csv/` to `archive/` first and checks row counts after.

### Open items (historical — resolved in v2.1 except robots.txt)

- [x] Confirm how `signed_in` is written in current live_csv (`true`/`false` assumed).
- [x] List the `ai_answer_format` values in use and add them to `csv/2_SCHEMA.md`.
- [x] Confirm the role of "check · collector" in README.
- [ ] Verify robots.txt / CDN access for AI bots (from study notes; not a pipeline task).

---

## Legacy storage migration checklist (historical — completed 2026-10-27; superseded by GitHub-only workflow)

**Prepare**
- [x] Create folders: `instructions/capture/`, `instructions/csv/`, `archive/`, `reports/`.

**Archive the v1 instructions** (move, don't delete) to `archive/instructions_v1/`
- [ ] Still pending if old v1 files remain in legacy storage.

**Upload v2** (as plain `.md` / `.csv` files)
- [x] `README.md` → root
- [x] `1_CHECKLIST.md`, `2_RUNBOOK.md`, `3_APP_GUIDE.md` → `instructions/capture/`
- [x] `1_BUILD_AND_LOAD.md`, `2_SCHEMA.md` → `instructions/csv/`
- [x] `CHANGELOG.md` → `instructions/`
- [x] `brand_aliases_v3.csv` → `inputs/`

**Other moves**
- [ ] Study notes → `reports/` (if present)
- [x] Leave existing `runs/` folders as they are

**live_csv cleanup**
- [x] One-time migration done 2026-10-27 (split `run_id`; facts archived).

**Check**
- [x] README paths match repo folders (`capture/`, `csv/`).
- [ ] Give bots the new opener when starting a task.

---

## Incident history (from v1 runbook)

### 2026-10-26 · delta dry-run
- A bot drafted its own prompts when asked to "add 10 prompts". → Rule: never invent prompts; ask for rows.
- Rewriting the whole prompts CSV risked truncation. → Rule: delta files; master merged only with a row-count check.
- Automation couldn't always open Incognito; runs were labelled Incognito when they used the shared profile. → Rule: record the session actually used. (v2: shared profile is acceptable for ChatGPT/Gemini.)
- ChatGPT guest sessions silently failed after the first prompt, and the bot kept sending. → Rule: stop the app on first silent send-fail.
- Runs were scored as USA while egress was India. → Rule: check IP in the capture browser; ask before proceeding non-US.
- Captures left only on the local box were reported as done. → Rule: done means committed and pushed.

### 2026-10-26/27 · Claude and ChatGPT runs
- Signed-in Claude chats inherited account history. → Rule: Claude Incognito chat toggle for every prompt.
- Claude Free, 1 tab sequential, took ~36 min for 11 prompts. → Guidance: 3 tabs when limits allow.
- Clipboard unavailable on the box; condensed text was saved as answers. → Rule: full verbatim via `innerText`; never summaries.
- A loop overwrote several raw folders at once. → Rule: write one folder at a time.
- "Computer offline" mid-run aborted an already-approved IN run. → Rule: keep going if IN was approved; record actual IP.
- `meta.txt` written instead of `meta.json`. → Rule: JSON only.
