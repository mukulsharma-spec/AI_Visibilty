# Build and Load Instructions

This document describes how to build and load CSV data for AI Visibility capture runs.

## Prerequisites

- Access to the GitHub repository (source of truth)
- Python 3.9+ with pandas installed
- Write access to the output directory

## Input Files

All input files are located in the `inputs/` directory:

### Master Files (inputs/ root)

These are the canonical, versioned files used for standard capture runs:

| File | Description |
|------|-------------|
| `prompts_v3_final.csv` | Master prompt list for capture |
| `brand_aliases_v3.csv` | Brand canonical names and aliases |

### Run Lists (inputs/run_lists/)

One-off and delta prompt lists for specific capture runs:

| File | Description |
|------|-------------|
| `prompts_delta_2026-10-27.csv` | Delta prompts from 2026-10-27 |
| `prompts_delta_2026-10-27_br20.csv` | Delta prompts (br20 batch) |
| `prompts_nosuffix_2026-10-28_12.csv` | No-suffix prompts from 2026-10-28 |

## Loading Data

### Standard Capture Run

```bash
python scripts/capture.py \
  --prompts inputs/prompts_v3_final.csv \
  --brands inputs/brand_aliases_v3.csv \
  --output outputs/answers.csv
```

### Delta/One-off Run

```bash
python scripts/capture.py \
  --prompts inputs/run_lists/prompts_delta_2026-10-27.csv \
  --brands inputs/brand_aliases_v3.csv \
  --output outputs/answers_delta_2026-10-27.csv
```

## Output Schema

Output files follow the v2.2 schema with 30 columns. See [2_SCHEMA.md](./2_SCHEMA.md) for full column definitions.

Key changes in v2.2:
- `ai_angara_rank` (int or blank): 1-based rank position
- `ai_angara_rank_n` (int or blank): Total rank slots

## Validation

After loading, validate the output:

```bash
python scripts/validate.py outputs/answers.csv --schema v2.2
```

Validation checks:
1. Column count equals 30
2. Required fields are non-empty
3. Rank fields are consistent (both blank or both populated)
4. Brand references resolve to known brands/aliases

## Troubleshooting

### Column Count Mismatch

If you see "Expected 30 columns, got 29", you may be using a v2.1 output. Check the schema version in the `ai_analysis_version` column.

### Missing Brand Aliases

Ensure `brand_aliases_v3.csv` is up to date. Pull latest from GitHub:

```bash
git pull origin main
```
