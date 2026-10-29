# Capture Runbook

Step-by-step operational guide for executing AI Visibility capture runs.

## Overview

This runbook covers the standard operating procedure for capture runs using the v2.2 schema.

## Source of Truth

**GitHub** is the source of truth for all configuration, prompts, and documentation. Always pull the latest before starting a run.

## File Organization

### Master Files (inputs/)

Located at the root of `inputs/`:

| File | Purpose |
|------|---------|
| `prompts_v3_final.csv` | Canonical prompt list for standard runs |
| `brand_aliases_v3.csv` | Brand name mappings and aliases |

### Run Lists (inputs/run_lists/)

One-off and delta files for specific capture runs:

| File | Purpose |
|------|---------|
| `prompts_delta_2026-10-27.csv` | Delta additions from 2026-10-27 |
| `prompts_delta_2026-10-27_br20.csv` | BR20 batch delta prompts |
| `prompts_nosuffix_2026-10-28_12.csv` | No-suffix variant prompts |

## Standard Run Procedure

### Step 1: Prepare Environment

```bash
# Clone or pull latest
git clone https://github.com/[org]/AI_Visibilty.git
cd AI_Visibilty
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Verify input files
ls -la inputs/
ls -la inputs/run_lists/
```

### Step 2: Configure Run

Set environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export RUN_ID="run_$(date +%Y-%m-%d)"
```

### Step 3: Execute Capture

For a standard full run:

```bash
python scripts/capture.py \
  --prompts inputs/prompts_v3_final.csv \
  --brands inputs/brand_aliases_v3.csv \
  --output outputs/answers_${RUN_ID}.csv \
  --schema v2.2
```

For a delta run:

```bash
python scripts/capture.py \
  --prompts inputs/run_lists/prompts_delta_2026-10-27.csv \
  --brands inputs/brand_aliases_v3.csv \
  --output outputs/answers_delta_${RUN_ID}.csv \
  --schema v2.2
```

### Step 4: Validate Output

```bash
python scripts/validate.py outputs/answers_${RUN_ID}.csv --schema v2.2
```

Expected validation output:
```
Schema version: v2.2
Column count: 30 ✓
Required fields: OK ✓
Rank field consistency: OK ✓
Brand resolution: OK ✓
```

### Step 5: Post-Processing

```bash
# Generate summary statistics
python scripts/analyze.py outputs/answers_${RUN_ID}.csv --summary

# Archive run
cp outputs/answers_${RUN_ID}.csv archive/
```

## Schema v2.2 Notes

### Rank Fields

The v2.2 schema splits the previous `ai_angara_rank_of_n` string field into two integer fields:

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `ai_angara_rank` | int or blank | `2` | 1-based rank position |
| `ai_angara_rank_n` | int or blank | `5` | Total slots (was "of N") |

Previously: `"2 of 5"` (string)
Now: `ai_angara_rank=2`, `ai_angara_rank_n=5`

### Column Count

- v2.1: 29 columns
- v2.2: 30 columns

### Migration Note

`live_csv` may still be on v2.1 until migration is completed. Check `ai_analysis_version` column to confirm schema version.

## Troubleshooting

### Rate Limit Errors

If you encounter rate limits:
1. Check current quota usage with provider
2. Reduce batch size in capture config
3. Add delays between requests

### Schema Mismatch

If validation fails on column count:
1. Verify you're using the v2.2 capture script
2. Check output file wasn't appended to a v2.1 file
3. Re-run with `--schema v2.2` flag

### Missing Prompts

If prompts aren't found:
1. Verify file path is correct
2. Check file encoding is UTF-8
3. Ensure header row is present

## Emergency Contacts

- Data team: [data-team@example.com]
- On-call: [oncall@example.com]
