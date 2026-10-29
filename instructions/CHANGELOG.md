# Changelog

All notable changes to the AI Visibility project are documented in this file.

## [v2.2] - 2026-10-29

### Schema Changes
- **BREAKING**: Split `ai_angara_rank_of_n` (string) into two separate fields:
  - `ai_angara_rank` (int or blank): 1-based rank position
  - `ai_angara_rank_n` (int or blank): Total number of rank slots (was "of N")
- Column count in `answers.csv` increased from 29 to 30

### Repository Structure
- Master prompt and brand alias files now live at `inputs/` root:
  - `inputs/prompts_v3_final.csv`
  - `inputs/brand_aliases_v3.csv`
- One-off/delta run lists moved to `inputs/run_lists/`:
  - `prompts_delta_2026-10-27.csv`
  - `prompts_delta_2026-10-27_br20.csv`
  - `prompts_nosuffix_2026-10-28_12.csv`

### Documentation
- Updated all docs to reflect v2.2 schema and new file locations
- GitHub is now the source of truth (previously Google Drive)

### Migration Notes
- `live_csv` may remain on v2.1 until data migration is completed
- No automated data migration is performed; coordinate with data team if needed

---

## [v2.1] - 2026-10-15

### Schema
- Initial documented schema with 29 columns
- `ai_angara_rank_of_n` as combined string field ("X of N")

---

## [v2.0] - 2026-09-01

### Initial Release
- Established CSV-based capture pipeline
- Core answer analysis fields defined
