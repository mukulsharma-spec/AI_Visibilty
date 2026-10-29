# CSV Schema v2.2 (2026-10-29)

This document defines the schema for `answers.csv` used in AI Visibility capture and analysis.

## Schema Version

- **Current version**: v2.2
- **Column count**: 30

> **Note**: `live_csv` may still be on v2.1 until migration is completed.

## answers.csv Columns (30 total)

| # | Column Name | Type | Description |
|---|-------------|------|-------------|
| 1 | `answer_id` | string | Unique identifier for this answer |
| 2 | `prompt_id` | string | Reference to the prompt that generated this answer |
| 3 | `prompt_text` | string | The full text of the prompt |
| 4 | `category` | string | Category classification of the prompt |
| 5 | `brand` | string | Canonical brand name |
| 6 | `locale` | string | Locale code (e.g., en-US) |
| 7 | `model` | string | AI model identifier |
| 8 | `model_version` | string | Version of the AI model |
| 9 | `provider` | string | AI provider (e.g., OpenAI, Anthropic) |
| 10 | `answer_text` | string | Full text of the AI response |
| 11 | `answer_timestamp` | datetime | When the answer was captured |
| 12 | `run_id` | string | Identifier for the capture run |
| 13 | `run_batch` | string | Batch identifier within the run |
| 14 | `latency_ms` | int | Response latency in milliseconds |
| 15 | `token_count_prompt` | int | Number of tokens in the prompt |
| 16 | `token_count_completion` | int | Number of tokens in the completion |
| 17 | `ai_brand_mentioned` | boolean | Whether the brand was mentioned in the answer |
| 18 | `ai_brand_position` | int or blank | Position of first brand mention (1-indexed) |
| 19 | `ai_sentiment` | string | Detected sentiment (positive, neutral, negative) |
| 20 | `ai_sentiment_score` | float | Sentiment confidence score (-1.0 to 1.0) |
| 21 | `ai_competitors_mentioned` | string | Comma-separated list of competitor brands mentioned |
| 22 | `ai_competitor_count` | int | Count of competitor mentions |
| 23 | `ai_recommendation_type` | string | Type of recommendation (direct, indirect, none) |
| 24 | `ai_angara_rank` | int or blank | 1-based rank of the brand in recommendations (blank if not ranked) |
| 25 | `ai_angara_rank_n` | int or blank | Total number of rank slots (N in "rank X of N"; blank if not ranked) |
| 26 | `ai_citation_present` | boolean | Whether citations are present in the answer |
| 27 | `ai_citation_urls` | string | Comma-separated list of cited URLs |
| 28 | `ai_hallucination_flag` | boolean | Flagged for potential hallucination |
| 29 | `ai_analysis_version` | string | Version of the analysis pipeline |
| 30 | `notes` | string | Optional notes or flags |

## Changes from v2.1

### Rank field split

The previous `ai_angara_rank_of_n` column (string format like "2 of 5") has been replaced with two separate columns:

- **`ai_angara_rank`** (column 24): 1-based integer representing the brand's rank position, or blank if not ranked
- **`ai_angara_rank_n`** (column 25): Integer representing the total number of rank slots (the "N" in the old "X of N" format), or blank if not ranked

This change enables easier numeric sorting and filtering on rank data.

### Column count

- v2.1: 29 columns
- v2.2: 30 columns

## Validation Rules

1. `answer_id` must be unique across all rows
2. `prompt_id` must reference a valid prompt in `prompts_v3_final.csv`
3. `brand` should match a canonical brand or alias in `brand_aliases_v3.csv`
4. `ai_angara_rank` when present must be >= 1 and <= `ai_angara_rank_n`
5. `ai_angara_rank_n` when present must be >= 1
6. Both rank fields should be blank together or populated together

## Example Row

```csv
ans_001,prm_042,"Best CRM software?",software,Salesforce,en-US,gpt-4,gpt-4-0613,OpenAI,"Based on my analysis...",2026-10-29T10:30:00Z,run_2026-10-29,batch_01,1250,45,320,true,2,positive,0.85,"HubSpot,Zoho",2,direct,2,5,true,"https://...",false,v2.2,""
```
