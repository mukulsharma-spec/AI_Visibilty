# AI Visibility

AI Visibility capture and analysis pipeline for tracking brand mentions and rankings in AI-generated responses.

## Source of Truth

**GitHub** is the source of truth for all configuration, prompts, brand aliases, and documentation.

## Repository Structure

```
AI_Visibilty/
├── README.md
├── inputs/
│   ├── prompts_v3_final.csv      # Master prompt list
│   ├── brand_aliases_v3.csv      # Brand canonical names and aliases
│   └── run_lists/                # One-off and delta run lists
│       ├── prompts_delta_2026-10-27.csv
│       ├── prompts_delta_2026-10-27_br20.csv
│       └── prompts_nosuffix_2026-10-28_12.csv
└── instructions/
    ├── CHANGELOG.md              # Version history
    ├── csv/
    │   ├── 1_BUILD_AND_LOAD.md   # Data loading instructions
    │   └── 2_SCHEMA.md           # CSV schema definition (v2.2)
    └── capture/
        ├── 1_CHECKLIST.md        # Pre-flight checklist
        └── 2_RUNBOOK.md          # Operational runbook
```

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/[org]/AI_Visibilty.git
   cd AI_Visibilty
   ```

2. Review the capture checklist:
   - [Capture Checklist](instructions/capture/1_CHECKLIST.md)

3. Run a capture:
   ```bash
   python scripts/capture.py \
     --prompts inputs/prompts_v3_final.csv \
     --brands inputs/brand_aliases_v3.csv \
     --output outputs/answers.csv
   ```

## Schema Version

**Current schema: v2.2** (2026-10-29)

Key features of v2.2:
- 30 columns in `answers.csv`
- Rank fields split into `ai_angara_rank` (int) and `ai_angara_rank_n` (int)
- See [Schema Documentation](instructions/csv/2_SCHEMA.md) for details

> **Note**: `live_csv` may still be on v2.1 until migration is completed.

## Input Files

### Master Files (`inputs/`)

| File | Description |
|------|-------------|
| `prompts_v3_final.csv` | Canonical prompt list for capture runs |
| `brand_aliases_v3.csv` | Brand names and alias mappings |

### Run Lists (`inputs/run_lists/`)

One-off and delta prompt lists for specific capture runs. These are not part of the master prompt set.

## Documentation

- [Changelog](instructions/CHANGELOG.md) - Version history and migration notes
- [Build and Load](instructions/csv/1_BUILD_AND_LOAD.md) - Data loading instructions
- [Schema](instructions/csv/2_SCHEMA.md) - CSV column definitions (v2.2)
- [Checklist](instructions/capture/1_CHECKLIST.md) - Pre-flight checklist
- [Runbook](instructions/capture/2_RUNBOOK.md) - Operational procedures

## Contributing

1. Create a feature branch from `main`
2. Make changes following existing conventions
3. Submit a pull request with clear description
4. Reference any related issues with `#<issue-number>`
