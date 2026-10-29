# CSV Schema

csv/2_SCHEMA v2.3 · 2026-10-29

The three dashboard CSVs: `answers.csv`, `brand_mentions.csv`, `citations.csv`. The same three files exist in each `runs/<run_id>/csv/` (one run) and in `live_csv/` (all runs appended). There are no other CSV tables in the pipeline.

How to fill each column is in `1_BUILD_AND_LOAD.md`. Names (`run_id`, `run_key`) are defined in `README.md`.

**Kind** column below:
- **M** = measured by script from raw files
- **J** = judged by reading the answer
- **J\*** = judged and required (never blank)

---

## 1. Shared rules

**File format**
- UTF-8, comma-separated, one header row, `\n` line endings.
- Quote any field containing a comma, quote or line break (standard CSV quoting).
- Blank value = empty field. Never write `null`, `NaN` or `None`.
- No extra columns, no index column. Columns in exactly the order listed.

**Key columns** (first six columns of every file, in this order)

| # | Column | Type | Example |
|---|---|---|---|
| 1 | `run_id` | string | `2026-10-27_delta_v3` |
| 2 | `run_key` | string | `claude\|CH03\|r1\|t1` |
| 3 | `app` | string | `chatgpt`, `claude`, `gemini` |
| 4 | `prompt_id` | string | `CH03` |
| 5 | `repeat` | string | `r1` |
| 6 | `turn` | integer | `1` or `2` |

`turn` is the number `1`, while `run_key` contains `t1`. `prompt_id` is only the prompt id — never encode bot name or date in it. Date/batch lives in `run_id`; bot identity lives in `source` / capture meta.

**Uniqueness**

| File | Unique on |
|---|---|
| answers.csv | `run_id` + `run_key` |
| brand_mentions.csv | `run_id` + `run_key` + `brand` |
| citations.csv | `run_id` + `run_key` + `link_order` |

**Value types**
- `0/1`: integer flag.
- `true/false`: lowercase text (never `True`/`False` or `1`/`0`).
- Positions (`*_char_pos`): 0-based integer, blank if not found.
- Timestamps: `YYYY-MM-DD HH:MM:SS`, UTC.

---

## 2. answers.csv: 30 columns, one row per answer

| # | Column | Kind | Type | Meaning / allowed values |
|---|---|---|---|---|
| 1–6 | key columns | M | | Section 1 |
| 7 | `prompt` | M | string | Exact text sent (with USA suffix on turn 1) |
| 8 | `captured_at_utc` | M | timestamp | When captured |
| 9 | `signed_in` | M | true/false | Signed in to the app (lowercase) |
| 10 | `session` | M | string | `incognito`, `signed_out_shared_profile`, `claude_incognito_chat`; blank for older runs |
| 11 | `egress_country` | M | string | Two-letter country, e.g. `US`, `IN`; blank if unknown |
| 12 | `source` | M | string | `grok_bot_ui`, `parallel_test`, `schedule`, `api` |
| 13 | `text_source` | M | string | `answer` or `page_copy` |
| 14 | `has_raw_folder` | M | 0/1 | Raw folder exists |
| 15 | `answer_chars` | M | integer | Length of the answer body |
| 16 | `web_search_marker` | M | 0/1 | App searched the web or showed sources |
| 17 | `angara_in_text` | M | 0/1 | "angara" appears in the body |
| 18 | `angara_mention_count` | M | integer | Number of "angara" matches |
| 19 | `angara_first_char_pos` | M | integer/blank | Position of first match |
| 20 | `n_brands_found` | M | integer | Alias-list brands found in the body |
| 21 | `n_links` | M | integer | Citation rows for this answer |
| 22 | `angara_link_present` | M | 0/1 | Any citation on angara.com |
| 23 | `ai_answer_format` | J\* | string | **Allowed values only** (section 2a). New values need the human's OK, then add them here. |
| 24 | `ai_n_recommended` | J\* | integer | Brands with role `recommended` |
| 25 | `ai_n_rank_slots` | J | integer/blank | Highest `published_rank` used |
| 26 | `ai_angara_role` | J\* | string | `recommended`, `mentioned`, `compared_against`, `cited_only`, `absent` |
| 27 | `ai_angara_published_rank` | J | integer/blank | Angara's rank |
| 28 | `ai_angara_rank` | J | integer/blank | 1-based rank position (blank if not ranked) |
| 29 | `ai_angara_rank_n` | J | integer/blank | Total rank slots, was "of N" (blank if not ranked) |
| 30 | `ai_top1_brand` | J | string/blank | Rank-1 brand(s), joined by `;` |

### 2a. Allowed `ai_answer_format` values (locked 2026-10-27)

From live `answers.csv` at migration. Do not invent new labels without human approval.

- `bullets`
- `bullets_by_category`
- `bullets_by_price_tier`
- `checklist`
- `clarifying_question`
- `comparison`
- `comparison_table`
- `headings`
- `local_map_list`
- `mixed`
- `numbered_headings`
- `numbered_list`
- `paragraphs`
- `paragraphs_bullets`
- `paragraphs_by_category`
- `paragraphs_by_price_tier`
- `product_cards`
- `product_cards_text_missing`
- `prose_bullets`
- `prose_by_category`
- `prose_paragraphs`
- `table`

---

## 3. brand_mentions.csv: 20 columns, one row per brand in an answer

| # | Column | Kind | Type | Meaning / allowed values |
|---|---|---|---|---|
| 1–6 | key columns | M | | Section 1 |
| 7 | `brand` | M/J | string | Alias-list name (`fact_row=1`) or name as written (`fact_row=0`) |
| 8 | `fact_row` | M | 0/1 | `1` = matched by the alias list; `0` = added by reading |
| 9 | `mention_count` | M | integer/blank | Number of matches; blank when `fact_row=0` |
| 10 | `first_char_pos` | M | integer/blank | Position of first match; blank when `fact_row=0` |
| 11 | `order_of_first_appearance` | M | integer/blank | 1 = first brand in the text (not a rank); blank when `fact_row=0` |
| 12 | `text_source` | M | string/blank | `answer` or `page_copy`; blank when `fact_row=0` |
| 13 | `published_rank` | J | integer/blank | Only for `recommended` |
| 14 | `tie` | J\* | 0/1 | Shares its rank slot |
| 15 | `role` | J\* | string | `recommended`, `mentioned`, `compared_against`, `cited_only`, `false_match` |
| 16 | `in_product_card` | J\* | 0/1 | Shown in a product card |
| 17 | `price_shown_usd` | J | string/blank | Exact price text |
| 18 | `claim` | J\* | string | Why named, max 15 words |
| 19 | `sentiment` | J\* | string | `positive`, `neutral`, `negative` |
| 20 | `confidence` | J\* | string | `high`, `medium`, `low` |

---

## 4. citations.csv: 11 columns, one row per outbound link

| # | Column | Kind | Type | Meaning / allowed values |
|---|---|---|---|---|
| 1–6 | key columns | M | | Section 1 |
| 7 | `link_order` | M | integer | 1-based order in the HTML |
| 8 | `url` | M | string/blank | Full URL; blank for Gemini name-only chips |
| 9 | `domain` | M | string | Registrable domain, e.g. `angara.com` |
| 10 | `is_angara` | M | 0/1 | Domain is angara.com |
| 11 | `source_file` | M | string | `html` or `html_chip` |

Within one answer, keep each URL only once. Drop app/support links (`chatgpt.com`, `chat.openai.com`, `claude.ai`, `gemini.google.com`, Google account/support pages).

---

## 5. Dashboard

| Dashboard panel | Needs |
|---|---|
| Mention rate, categories, citations | Measured columns |
| Recommended, rank, Competitors, Cards | Judged columns |

Category comes from `inputs/prompts_v3_final.csv` (and delta files), joined on `prompt_id`.

---

## 6. Changes from v2.1 (v2.2)

| Change | Why |
|---|---|
| Split `ai_angara_rank_of_n` (string) into `ai_angara_rank` (int) + `ai_angara_rank_n` (int) | Enables numeric sorting/filtering on rank data |
| answers.csv column count 29 → 30 | Result of the rank field split |

**Rank field validation (v2.2)**:
- `ai_angara_rank` when present must be >= 1 and <= `ai_angara_rank_n`
- `ai_angara_rank_n` when present must be >= 1
- Both rank fields should be blank together or populated together

> **Note**: `live_csv/` may remain on v2.1 until migration is completed. Check `ai_analysis_version` column if present, or column count (29 = v2.1, 30 = v2.2).

---

## 7. Changes from v1

| Change | Why |
|---|---|
| One set of three files; no separate facts / labels / merged tables | Bots build the dashboard shape directly from raw |
| `run_id` added as column 1 of every file | v1 keys had no date, so a second week's rows would duplicate the first week's |
| `session`, `egress_country`, `source` added to answers (after `signed_in`) | Filter out non-US, signed-in or test captures on the dashboard |
| `source_file` value `html_chip` added | Count Gemini citations that have no link |
| Column order fixed (v1 allowed brand_mentions in any order) | Appending only works safely when order matches |
| answers 30 columns (v1: 25); brand_mentions 20 (v1: 19); citations 11 (v1: 10) | Result of the above |
| Allowed `ai_answer_format` list locked (section 2a) | Stop inventing new format labels |

## 8. One-time migration of current live_csv (needs the human's yes)

Current `live_csv/` holds v1 files (`answers.csv`, `brand_mentions.csv`, `citations.csv`) plus facts-only files (`*_facts.csv`).

1. Back up the whole folder to `archive/live_csv_backup_2026-10-27/`.
2. Move the three `*_facts.csv` files to `archive/live_csv_facts_only_v1/`.
3. In the three v1 files, add the new columns in their v2 positions:
   - **`run_id` split by capture date / known delta IDs — do not label every row baseline:**
     - Rows captured on `2026-10-22` or `2026-10-23` (or otherwise not in the 2026-10-27 delta) → `2026-10-baseline_v3`
     - Rows for the 2026-10-27 delta prompts (`CH03`, `CP10`, `SG13`, `OC18`, `TR13`, `IM12`) / `captured_at_utc` on 2026-10-27 → `2026-10-27_delta_v3`
   - `session` = blank, `egress_country` = `IN`, `source` = `grok_bot_ui`
   - Rewrite `signed_in` to lowercase `true`/`false`
4. Put brand_mentions columns in the v2 order (add `run_id` first; remaining columns already match).
5. Remove exact duplicate rows, then check uniqueness (section 1). Report any keys still duplicated instead of guessing which row to keep.
6. Report row counts before and after for each file, and counts per `run_id`.
