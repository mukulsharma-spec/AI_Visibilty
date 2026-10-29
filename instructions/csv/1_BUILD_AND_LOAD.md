# Build & Load CSVs

csv/1_BUILD_AND_LOAD v2.2 · 2026-10-29

How raw captures become the three dashboard CSVs. **Read "All CSV tasks", then only the section for your task.** Column names, order and allowed values are in `2_SCHEMA.md`; this file says how to fill them. Names (`run_id`, `run_key`, folders) are in `README.md`.

```
runs/<run_id>/raw/        (immutable, from Capture)
        │  Build CSVs
        ▼
runs/<run_id>/csv/        answers.csv, brand_mentions.csv, citations.csv  (SCHEMA shape)
        │  Load (human approval)
        ▼
live_csv/                 same three files, all runs appended (SCHEMA v2)
```

Build and Load are separate tasks. When yours is done, report to the human and stop.

---

# All CSV tasks

## Inputs

| Input | Used for |
|---|---|
| `runs/<run_id>/raw/<app>/<raw folder>/` | `meta.json`, `answer.txt`, `answer.html` or `answer.html.gz` |
| `runs/<run_id>/run_info_<app>.json` | Which IDs were assigned, captured, failed, discarded |
| `inputs/prompts_v3_final.csv` + delta files from `inputs/run_lists/` | Prompt text |
| `inputs/brand_aliases_v3.csv` | Brand match patterns (Build only) |

## Rules

1. **Never change anything in `raw/`.**
2. **Skip every raw folder whose name contains `__discarded`.**
3. Build writes only inside `runs/<run_id>/csv/`. Those files can be rebuilt and overwritten until the run is loaded.
4. Every row carries `run_id` and `run_key` in the SCHEMA format. `prompt_id` is the prompt id only — never put bot name or date in it.
5. Never invent columns or values outside the SCHEMA vocabularies (including the locked `ai_answer_format` list in `2_SCHEMA.md` §2a). If something doesn't fit, stop and ask.
6. In CSV files, write `signed_in` as lowercase text `true` or `false` (never `True`/`False` or `1`/`0`). JSON booleans in `meta.json` are fine; coerce when writing the CSV.

## Older runs

Runs captured before the v2 instructions use older formats. Read them, but write CSVs in the current format.

| Old | Convert to |
|---|---|
| Layout `runs/<run>/<app>/raw/<run_key>/` | Same data; `run_id` = the run folder name as it is (for example `2026-10-27_delta_v3`) |
| Folder names with `\|` and a date: `claude\|CH03\|r1\|1\|2026-10-26` | `run_key` = `claude\|CH03\|r1\|t1` |
| `meta.json` keys `id`, `platform` | `prompt_id`, `app` |
| No `prompt_sent` in meta | `prompt_text` + ` I'm shopping in the USA.` for turn 1; `followup_text` for turn 2 |
| No `session` in meta | Blank; note it in `build_info.json` |
| `signed_in` as `True`/`False` | Lowercase `true`/`false` in the CSV |

**Already-loaded `live_csv/`:** migrated 2026-10-27 to SCHEMA v2. Existing `run_id` values are `2026-10-baseline_v3` (Oct 22–23) and `2026-10-27_delta_v3` (six delta prompts). Do not re-run the one-time migration in `2_SCHEMA.md` §7 unless the human asks.

---

# Build CSVs

## Output

`runs/<run_id>/csv/`: `answers.csv`, `brand_mentions.csv`, `citations.csv`, `build_info.json`.

Every column is one of two kinds (marked in `2_SCHEMA.md`):
- **Measured**: computed by script from the raw files. Exact and repeatable, no judgment.
- **Judged**: decided by reading the answer (role, rank, sentiment…).

Do all measured columns by script first (steps 1–4), then the judged columns (step 5).

## Step 1: List captures and get the answer body

- Every non-discarded raw folder in the run, for every app present.
- Body = `answer.txt` (`text_source=answer`). If missing or empty, use the visible text of `answer.html` (`text_source=page_copy`).

## Step 2: citations.csv (measured)

One row per outbound link in `answer.html` (decompress `.gz` first).

- Take `http`/`https` `href` values only.
- **Drop app links:** any URL on `chatgpt.com`, `chat.openai.com`, `openai.com`, `claude.ai`, `anthropic.com`, `gemini.google.com`, `accounts.google.com`, `support.google.com`, `policies.google.com`, plus `mailto:`, `javascript:` and `#` links.
- Keep the first occurrence of each exact URL; drop repeats within the same answer.
- `link_order` = 1-based order in the HTML after dropping.
- `domain` = registrable domain without `www.` (for example `blog.angara.com` → `angara.com`).
- `is_angara` = `1` if `domain` is `angara.com`.
- `source_file` = `html`.
- **Gemini chips without links:** one row per chip with `url` blank, `domain` from the chip label when it's a recognizable domain, `source_file` = `html_chip`.

## Step 3: brand_mentions.csv, measured columns

One row per brand whose pattern in `brand_aliases_v3.csv` matches the body (case-insensitive). Set `fact_row=1`.

- `mention_count` = number of matches.
- `first_char_pos` = 0-based start of the first match.
- `order_of_first_appearance`: sort matched brands by `first_char_pos`; 1 = earliest. This is **not** a rank.

## Step 4: answers.csv, measured columns

One row per raw folder.

| Column | How to fill |
|---|---|
| `run_id` | From the run folder / human; same for every row in this build |
| `prompt` | `meta.prompt_sent` (older runs: see "Older runs") |
| `captured_at_utc`, `session`, `egress_country`, `source` | Copy from `meta.json` (`source` defaults to `grok_bot_ui` if missing) |
| `signed_in` | From meta, written as lowercase `true`/`false` |
| `has_raw_folder` | `1` |
| `answer_chars` | Character length of the body |
| `web_search_marker` | `1` if `meta.web_search` is true. Older runs without it: ChatGPT = any link containing `utm_source=chatgpt.com`; Claude = "Searched the web" in the page; Gemini = a citation or source chip in the HTML |
| `angara_in_text`, `angara_mention_count`, `angara_first_char_pos` | Case-insensitive match of `angara` in the body; position 0-based, blank if none |
| `n_brands_found` | Rows in `brand_mentions.csv` with `fact_row=1` for this answer |
| `n_links` | Rows in `citations.csv` for this answer |
| `angara_link_present` | `1` if any of those rows has `is_angara=1` |

## Step 5: Judged columns

Read each `answer.txt`. Never change a measured value.

**Brand rows**
- Fill the judged columns for every `fact_row=1` row.
- **Add a row with `fact_row=0`** for any store or brand the answer recommends that the alias list missed. Leave its measured columns blank. Use the name as written; check `live_csv/brand_mentions.csv` for an existing spelling first. Report new names so the human can add them to the alias list.

| Role | Use when |
|---|---|
| `recommended` | Presented as a place to buy or a pick for the shopper |
| `compared_against` | Named mainly as a comparison point ("unlike X…", "X is pricier") |
| `mentioned` | Named without being recommended or compared |
| `cited_only` | Appears only as a link or source, not in the answer text |
| `false_match` | The alias matched something else ("Amazon rainforest", "Tiffany setting", "practical target") |

| Field | Rule |
|---|---|
| `published_rank` | Only for `recommended`. Order the answer presents its picks: numbered list order, else the order picks appear. 1 = first. |
| `tie` | `1` when picks are presented as an equal group (for example one bullet naming two stores); tied brands share the rank number |
| `in_product_card` | `1` if the brand appears in a shopping or product card |
| `price_shown_usd` | Exact price text from the answer for that brand, else blank |
| `claim` | Why the answer names the brand, paraphrased, max 15 words |
| `sentiment` | `positive`, `neutral` or `negative`, as the answer presents the brand |
| `confidence` | `high`, `medium` or `low` for this row's judgments |

**Answer rows** (`ai_` columns)

| Field | Rule |
|---|---|
| `ai_answer_format` | **Only** a value from `2_SCHEMA.md` §2a (locked list). If none fits, stop and ask the human before inventing one. |
| `ai_n_recommended` | Brand rows with `role=recommended` |
| `ai_n_rank_slots` | Highest `published_rank` used |
| `ai_angara_role` | Angara's role, or `absent` if Angara isn't in the answer |
| `ai_angara_published_rank` | Angara's rank, blank if not recommended |
| `ai_angara_rank` | Angara's rank as 1-based integer; blank if not ranked |
| `ai_angara_rank_n` | Total rank slots (was `ai_n_rank_slots`); blank if not ranked |
| `ai_top1_brand` | Brand(s) with `published_rank=1`, joined by `;` |

## Step 6: Check

- Column names and order match `2_SCHEMA.md` in all three files (30 / 20 / 11 columns).
- Rows in `answers.csv` = non-discarded raw folders.
- Every ID in each `run_info_<app>.json` `ids_captured` has its folder(s); list any mismatch.
- No duplicate keys (SCHEMA, "Uniqueness"): `(run_id, run_key)` etc.
- Every `run_key` in `brand_mentions.csv` and `citations.csv` exists in `answers.csv` for the same `run_id`.
- No blank `run_id`, `run_key` or judged column that the SCHEMA marks as required.
- Every `ai_answer_format` value is in SCHEMA §2a.
- `signed_in` values are only `true` or `false` (lowercase).

## Step 7: build_info.json

```json
{
  "run_id": "2026-10-27_delta_v3",
  "builder": "Grok Bot",
  "script_version": "build_csv v1",
  "built_at_utc": "2026-10-27 08:00:00",
  "apps": ["chatgpt"],
  "raw_folders_read": 10,
  "folders_skipped_discarded": 1,
  "rows": { "answers": 10, "brand_mentions": 71, "citations": 41 },
  "new_brand_names": ["Natural Sapphire Co."],
  "warnings": ["claude__TR04__r1__t1: answer.txt empty, used page_copy"]
}
```

## Step 8: Report and stop

Row counts, warnings, mismatches with `run_info`, new brand names. Do not load.

---

# Load

Appends a built run to `live_csv/`. **Needs the human's explicit yes.**

`live_csv/` already holds SCHEMA v2 files only (`answers.csv`, `brand_mentions.csv`, `citations.csv`). Facts-only backups live under `archive/live_csv_facts_only_v1/`.

## Before asking

- All Build checks (step 6) pass.
- No `(run_id, run_key)` from the run already exists in `live_csv/answers.csv`.

## Steps

1. Show the human: `run_id`, apps included, rows to add per file, check results.
2. After the yes, for each of the three files:
   1. Copy the current `live_csv/<file>` to `archive/live_csv_backup_<YYYY-MM-DD>/`.
   2. Append the run's rows (same column order as SCHEMA).
   3. Confirm new row count = old count + added rows.
   4. Upload/overwrite `live_csv/<file>` in place when possible (keep the file id); otherwise upload new and trash the old only after confirm.
3. Report new row counts, counts per `run_id`, and the backup location.

**A run can be loaded in parts** (for example ChatGPT today, Claude tomorrow), because rows are unique on `(run_id, run_key)`. Say so when asking for approval.

**Replacing a run that is already loaded** (after a rebuild) needs its own explicit yes: back up, remove that `run_id`'s rows from all three files, append the new rows, confirm counts.
