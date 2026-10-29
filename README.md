# Angara AI-Visibility: START HERE

README v2.3.1 · 2026-10-29

**Source of Truth**: GitHub branch **`Ai_visibility_source`** is the working source of truth for all configuration, prompts, brand aliases, captures, and documentation. Assistants read from and commit/push directly to `Ai_visibility_source`; no PR into `main` is required for day-to-day capture, CSV, or run hand-off unless a human explicitly asks. The `main` branch may lag behind.

Every bot reads this file first, every time. It tells you which other files to read for the task you were given. **Read only those files.** Opening instruction files outside your task wastes context and mixes in rules from other stages.

---

## What this study does

We measure how often ChatGPT, Claude and Gemini recommend Angara and its competitors to a USA jewelry shopper. Bots send a fixed set of prompts through each app's public chat interface and save the answers exactly as shown. Later, on request, those answers are turned into three CSV tables that feed the dashboard.

## The pipeline

| Stage | What happens | Output | Who starts it |
|---|---|---|---|
| 1. Capture | Send prompts, save answers | `runs/<run_id>/raw/` + `SUMMARY_<app>.md` + `run_info_<app>.json` | Human message |
| 2. Build CSVs | Turn raw answers into the 3 dashboard CSVs | `runs/<run_id>/csv/` (answers, brand_mentions, citations) | Human asks |
| 3. Load | Append those rows to the dashboard feed | `live_csv/` | Human approves |

**Stages never chain automatically.** When your stage is done, report to the human and stop. Start the next stage only when the human asks for it.

---

## Step 1: Find your task

| The human says something like | Your task |
|---|---|
| "run these IDs on ChatGPT", "capture", "delta run", "full run" | **Capture** |
| "build the CSVs", "parse", "make CSVs for this run" | **Build CSVs** |
| "load", "update live_csv", "push to dashboard" | **Load** |
| "add prompts", "new prompts" | **Add prompts** |
| "change the instructions", "update the rules" | **Edit instructions** |

If the message fits none of these, or more than one, ask the human before reading anything else.

## Step 2: Read only these files

**Capture**
1. `instructions/capture/1_CHECKLIST.md`
2. `instructions/capture/2_RUNBOOK.md`
3. `instructions/capture/3_APP_GUIDE.md`: the "All apps" section plus the section for your app only

Do not open anything in `instructions/csv/`. You will not touch CSVs.

**Build CSVs**
1. `instructions/csv/1_BUILD_AND_LOAD.md`: "All CSV tasks" + "Build CSVs" sections
2. `instructions/csv/2_SCHEMA.md` (includes the locked `ai_answer_format` list in §2a)
3. `inputs/brand_aliases_v3.csv`

**Load**
1. `instructions/csv/1_BUILD_AND_LOAD.md`: "All CSV tasks" + "Load" sections
2. `instructions/csv/2_SCHEMA.md`

**Add prompts**
1. `instructions/capture/2_RUNBOOK.md`: "Prompts" section

**Edit instructions**
1. This file, the file being changed, and `instructions/CHANGELOG.md`

---

## Names used in every stage

| Name | Format | Example |
|---|---|---|
| `prompt_id` | Prompt id only (from the prompts CSV). Never encode bot name or date. | `CH03` |
| `run_id` | `YYYY-MM-DD_<full\|delta>_<note>`: the run folder name and CSV batch id | `2026-10-27_delta_v3` |
| `run_key` | `{app}\|{prompt_id}\|{repeat}\|t{turn}`: stored in `meta.json` and every CSV | `claude\|CH03\|r1\|t1` |
| Raw folder name | `run_key` with `__` instead of `\|` | `claude__CH03__r1__t1` |
| Raw folder path | `runs/<run_id>/raw/<app>/<raw folder name>/` | `runs/2026-10-27_delta_v3/raw/claude/claude__CH03__r1__t1/` |

- `app` is one of `chatgpt`, `claude`, `gemini`.
- The date/batch lives in `run_id`, not in `run_key` or `prompt_id`.
- Bot identity lives in `meta.captured_by` and answers.`source`, not in ids.
- A `run_key` is unique within one run. Across runs, `(run_id, run_key)` is unique.
- Folder names never contain `|`, because pipes break zip files, Windows downloads and shell commands.

**Older runs** (created before README v2) use older names: the date inside `run_key` and pipes in folder names. Leave those raw folders as they are. The CSV build reads both forms. Current `live_csv/` is already SCHEMA v2 with split `run_id`s: `2026-10-baseline_v3` (Oct 22–23 captures) and `2026-10-27_delta_v3` (six new prompts × 3 apps).

### run_id naming

Format: `YYYY-MM-DD_<type>_<label>`

| Part | Rule | Example |
|---|---|---|
| YYYY-MM-DD | Date the capture starts | 2026-11-03 |
| `<type>` | `full` = whole core prompt set; `delta` = only some or new prompts | full |
| `<label>` | What the run is (table below) | w02 |

**Labels:**

| Run type | Label | Example run_id | Scored in trends? |
|---|---|---|---|
| Weekly core run | wNN (two digits) | 2026-11-03_full_w02 | Yes |
| New prompts added that week | wNN_new | 2026-11-03_delta_w02_new | Yes from that week on |
| Same-week repeat | Same run_id as that week's run; use repeat = r2, r3 | 2026-11-03_full_w02 (rows with r2) | Yes |
| Re-capture of failed prompts | wNN_fix | 2026-11-04_delta_w02_fix | Counts as that week |
| No-suffix test | nosuffix | 2026-11-04_delta_nosuffix | Never |
| US-egress test | usegress | 2026-11-05_full_usegress | Separate trend line |

**Rules:**
- Week numbers count from the baseline. Oct 22–27 data is week 1 (w01); first weekly rerun is w02.
- One wNN per week. Mid-week new prompts go in that week's `_new` run, not a new week number.
- Grok Bot proposes the run_id from capture date + next week number; human confirms before capture starts.
- Never rename a run_id once its rows are in `live_csv/`.
- Validation should reject any run_id that doesn't match this pattern (note for ops; no validator script unless one already exists).
- Existing runs stay as-is: `2026-10-baseline_v3`, `2026-10-27_delta_v3`, `2026-10-27_delta_br20`. Dashboard treats all three as week 1.
- Folder name under `runs/<run_id>/` IS the run_id; meta/SUMMARY/CSVs copy that name into the run_id column.

**Weekly workflow notes:**
- Append weekly into `live_csv/` (three files: answers.csv, brand_mentions.csv, citations.csv).
- Keep per-run copy in `runs/<run_id>/csv/`.
- Same-week repeats use r2/r3 in the repeat column, not a new run_id.
- Next week is still r1 with a new run_id.

---

## Folder layout

```
Angara_AI_visibility/
├── README.md                  ← this file
├── inputs/
│   ├── prompts_v3_final.csv   ← master prompt list (append rows only)
│   ├── brand_aliases_v3.csv   ← brand match list used by Build CSVs
│   └── run_lists/             ← one-off and delta run lists
│       ├── prompts_delta_2026-10-27.csv
│       ├── prompts_delta_2026-10-27_br20.csv
│       └── prompts_nosuffix_2026-10-28_12.csv
├── instructions/
│   ├── capture/               ← read for Capture only
│   │   ├── 1_CHECKLIST.md
│   │   ├── 2_RUNBOOK.md
│   │   └── 3_APP_GUIDE.md
│   ├── csv/                   ← read for Build CSVs and Load only
│   │   ├── 1_BUILD_AND_LOAD.md
│   │   └── 2_SCHEMA.md        ← v2.2: 30 columns with split rank fields
│   └── CHANGELOG.md           ← dated record of rule changes
├── runs/
│   └── <run_id>/
│       ├── run_info_<app>.json       ← one per app, written by that app's bot
│       ├── SUMMARY_<app>.md          ← one per app
│       ├── raw/<app>/<raw folder>/   ← immutable
│       └── csv/                      ← answers.csv, brand_mentions.csv, citations.csv, build_info.json
├── live_csv/                  ← dashboard feed: ONLY answers.csv, brand_mentions.csv, citations.csv (no metadata here)
├── reports/                   ← study findings for people; bots do not read
└── archive/                   ← superseded files / backups; bots do not read for capture
```

## Schema Version

**Current schema: v2.2** (2026-10-29)

Key changes in v2.2:
- 30 columns in `answers.csv` (was 29)
- Rank fields split: `ai_angara_rank` (int) + `ai_angara_rank_n` (int), replaces `ai_angara_rank_of_n` (string)
- See [Schema Documentation](instructions/csv/2_SCHEMA.md) for details

> **Note**: `live_csv/` may remain on v2.1 until migration is completed.

---

## Rules for every task

1. **Never invent** prompts, prompt IDs, CSV columns or folder structures.
2. **Never edit or delete** anything inside `runs/*/raw/`.
3. **Never write to `live_csv/`** without the human's explicit approval in the current chat.
4. **Nothing starts on its own.** Work starts only from a human message or a routine the human approved.
5. **If instructions conflict or are unclear, stop and ask.** Do not pick one yourself.
6. **Done means committed and pushed to `Ai_visibility_source`.** Files that exist only on the local machine are not done. Raw folders must be committed under `runs/<run_id>/raw/<app>/` and pushed to `Ai_visibility_source`; a tar/zip alone is not done. **No PR into `main` for routine ops—commit/push directly.**
7. **Prefer one push per session.** When Build follows Capture in the same session, batch `runs/<run_id>/raw/` + `SUMMARY_<app>.md` + `run_info_<app>.json` + `runs/<run_id>/csv/` into a single push. Loading `live_csv/` requires a human "yes" first; after that, push `live_csv/` changes (plus any archive backup) to `Ai_visibility_source`—a second push is acceptable if needed.

---

## People and bots

| Name | Role |
|---|---|
| Human (M) | Approves runs, egress/VPN, Claude sign-in, CSV loads and any structural change |
| Grok Bot | Primary collector |
| @A | Second collector for parallel capture |
| check · collector | Third collector (same shared box; one bot per app by default) |

All bots run on one shared Linux machine in Jaipur, India. They share files, tools and egress IP; each has its own desktop and browser. Default split: one bot per app.
