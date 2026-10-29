# Capture Checklist

Pre-flight checklist for AI Visibility capture runs.

## Before Starting

### 1. Repository Sync

- [ ] Pull latest from GitHub (source of truth)
  ```bash
  git pull origin main
  ```

### 2. Input Files

Master files at `inputs/` root:
- [ ] `inputs/prompts_v3_final.csv` exists and is up to date
- [ ] `inputs/brand_aliases_v3.csv` exists and is up to date

For delta/one-off runs, check `inputs/run_lists/`:
- [ ] Confirm the correct run list file exists
- [ ] Verify prompt format matches expected schema

### 3. Environment

- [ ] Python 3.9+ installed
- [ ] Required packages installed (`pip install -r requirements.txt`)
- [ ] API keys configured for target AI providers
- [ ] Sufficient API quota available

### 4. Output Configuration

- [ ] Output directory exists and is writable
- [ ] Disk space available for expected output size
- [ ] Confirm output filename convention

## During Capture

- [ ] Monitor for rate limit errors
- [ ] Check log output for failures
- [ ] Verify incremental progress is being saved

## After Capture

### 5. Validation

- [ ] Run validation script against output
  ```bash
  python scripts/validate.py outputs/answers.csv --schema v2.2
  ```
- [ ] Verify column count is 30 (v2.2 schema)
- [ ] Check `ai_angara_rank` and `ai_angara_rank_n` fields are properly populated
- [ ] Sample-check a few rows for data quality

### 6. Documentation

- [ ] Log run metadata (date, prompt file used, model versions)
- [ ] Note any errors or anomalies
- [ ] Update run tracking sheet if applicable

## Schema Quick Reference

v2.2 schema (30 columns):
- Rank fields split: `ai_angara_rank` (1-based int) + `ai_angara_rank_n` (total slots)
- See `instructions/csv/2_SCHEMA.md` for full details

## File Locations Summary

```
inputs/
├── prompts_v3_final.csv      # Master prompts
├── brand_aliases_v3.csv      # Brand aliases
└── run_lists/
    ├── prompts_delta_*.csv   # Delta run lists
    └── prompts_nosuffix_*.csv # Special run lists
```
