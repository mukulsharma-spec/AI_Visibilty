# App Capture Guide

capture/3_APP_GUIDE v2.3.1 · 2026-10-29

What to click and what to save. **Read Part 1 (All apps), then only the section for your app in Part 2.** Policy (sessions, egress, failures) is in `2_RUNBOOK.md`. Names are defined in `README.md`.

---

# Part 1: All apps

## 1.1 Before saving anything

The answer must be **completely finished**: no cursor, no "thinking" or "searching" line, the stop button has turned back into send, and the action icons (Copy etc.) are visible under the reply.

## 1.2 Files in every raw folder

Path: `runs/<run_id>/raw/<app>/<raw folder name>/` (for example `runs/2026-10-27_delta_v3/raw/claude/claude__CH03__r1__t1/`). Turn 2 gets its own folder ending `__t2`.

| File | Content |
|---|---|
| `meta.json` | Capture details (template in 1.4). JSON only. |
| `answer.txt` | The **full answer exactly as shown**. Never shortened, summarized or reworded. |
| `answer.html` | The reply's HTML (DOM). If over about 1 MB, save as `answer.html.gz` instead. |
| `shot_1.png` | Screenshot after the answer finished. Add `shot_2.png`, `shot_3.png`… by scrolling for long answers. |

**What goes in `answer.txt`:** only the assistant's reply. Leave out the prompt, the sidebar and status lines like "Searched the web", "Finding…" or "Worked for 48s". Record those in `meta.json` (`web_search`, `notes`) instead.

**Write one folder at a time**, with the shell, into the current folder only.

## 1.3 capture_quality

Use exactly one of these four values; put any detail in `notes`.

| Value | Meaning |
|---|---|
| `full_verbatim` | Complete text and the real reply HTML |
| `text_wrapped_html` | Complete text, but `answer.html` is only the text wrapped in `<pre>` or `<article>` |
| `partial` | Incomplete answer: clarifying widget, stalled, or cut off |
| `low` | Major gaps: stub HTML, missing content, or only a mid-stream screenshot |

## 1.4 meta.json template

```json
{
  "run_id": "2026-10-27_delta_v3",
  "run_key": "chatgpt|CH03|r1|t1",
  "app": "chatgpt",
  "prompt_id": "CH03",
  "repeat": "r1",
  "turn": 1,
  "prompt_sent": "<prompt_text for CH03 from the CSV> I'm shopping in the USA.",
  "source": "grok_bot_ui",
  "captured_by": "Grok Bot",
  "captured_at_utc": "2026-10-27 05:40:00",
  "signed_in": false,
  "session": "signed_out_shared_profile",
  "ip": "104.28.225.10",
  "egress_city": "Delhi",
  "egress_country": "IN",
  "currency_seen": "USD",
  "bot_check": false,
  "chat_url": "https://chatgpt.com/c/6ae038d5-12a8-83ea-8e0b-305df7653a0b",
  "web_search": true,
  "model_ui": "not shown (signed-out default)",
  "capture_quality": "text_wrapped_html",
  "notes": "answer.txt from page innerText (no clipboard); answer.html is <pre> wrapper; shot_1 viewport only."
}
```

| Field | Rule |
|---|---|
| `run_key` | `{app}\|{prompt_id}\|{repeat}\|t{turn}`; no date (date lives in `run_id`). `prompt_id` is the prompt id only — never bot name or date. |
| `turn` | Number: `1` or `2` |
| `prompt_sent` | Exact text you sent, including the USA suffix on turn 1 |
| `captured_by` | Your bot name: `Grok Bot`, `@A` or `check · collector` |
| `captured_at_utc` | `YYYY-MM-DD HH:MM:SS`, UTC |
| `signed_in` | JSON boolean in meta (`true`/`false`). Claude = true; ChatGPT/Gemini = false. Build CSVs write lowercase text `true`/`false` into `live_csv`. |
| `session` | `incognito`, `signed_out_shared_profile` or `claude_incognito_chat`: the one you **actually** used |
| `ip`, `egress_city`, `egress_country` | From the IP check in the capture browser; `null` if unknown |
| `currency_seen` | Currency shown in the answer (for example `USD`, `INR`); `null` if none |
| `bot_check` | `true` if a captcha or bot check appeared |
| `chat_url` | Address-bar URL, or `null` with the reason in `notes` |
| `web_search` | `true` if the reply shows searching, sources, citations or shopping cards |
| `model_ui` | Model name shown in the app, or `not shown` |
| `source` | `grok_bot_ui`, `parallel_test`, `schedule` or `api` |

## 1.5 Run files

After your last prompt, write two files in `runs/<run_id>/` (not inside `raw/`). If one app was split across two bots, only the lead bot writes them (Runbook, "Parallel bots").

**One-push batching:** if Build will happen in the same session, hold the push until Build finishes, then push `raw/` + run files + `csv/` together.

**`run_info_<app>.json`** (for the CSV build and the record)

```json
{
  "run_id": "2026-10-27_delta_v3",
  "app": "chatgpt",
  "mode": "delta",
  "source": "grok_bot_ui",
  "prompts_file": "inputs/prompts_v3_final.csv",
  "bots": ["Grok Bot"],
  "session": "signed_out_shared_profile",
  "egress": { "ip": "104.28.225.10", "city": "Delhi", "country": "IN", "in_approved_by_human": true },
  "model_ui": "not shown (signed-out default)",
  "ids_assigned": ["CH01", "CH02", "CH03"],
  "ids_captured": ["CH01", "CH03"],
  "ids_failed": [{ "id": "CH02", "reason": "silent_send_fail" }],
  "folders_discarded": [],
  "html_gzipped": [],
  "started_at_utc": "2026-10-27 05:30:00",
  "ended_at_utc": "2026-10-27 05:41:00",
  "guide_version": "capture/3_APP_GUIDE v2.1"
}
```

`ids_captured` counts a multi-turn prompt as captured only when both turns are saved.

**`SUMMARY_<app>.md`** (for the human), with these headings:

1. **Run**: `run_id`, app, mode, bot(s), start and end time (UTC)
2. **Captured**: IDs saved successfully
3. **Failed**: each ID with its reason
4. **Discarded and re-run**: each `__discarded_N` folder and why
5. **Session and egress**: session used; IP, city, country; whether IN was approved
6. **Quality caveats**: any `partial` or `low` captures, wrapped HTML, name-only citations, gzipped HTML, tar backup (if any)
7. **Repo path** to `runs/<run_id>/` and `runs/<run_id>/raw/<app>/` on `Ai_visibility_source` (must contain the expanded raw folders; tar-only commits are not done)

---

# Part 2: Per app

## ChatGPT

**Session:** signed out (Incognito or shared profile). New chat every prompt.

**Send**
1. Open `https://chatgpt.com`. Confirm you're signed out (a "Log in" button is visible, no account avatar).
2. Click **New chat**, or confirm the composer is empty.
3. Paste the turn-1 text and press **Send**.
4. **Check a chat was created:** the reply starts streaming and the address bar changes to a chat URL. If the composer clears with no reply and no new URL, that's a **silent send-fail**: stop ChatGPT and follow the Runbook, "Failures".
5. Wait until finished (1.1).
6. Multi-turn: send `followup_text` in the same chat, wait again.

**Save**
1. `answer.txt`: click the **Copy** icon under the reply and paste. Copy keeps product links as `Shop X (https://…)`. If the clipboard doesn't work, use the reply element's `innerText`.
2. `answer.html`: save the reply DOM so product cards and citation links are kept. If that's not possible, wrap the full text in `<pre>` and set `capture_quality=text_wrapped_html`.
3. Screenshots: `shot_1.png` after finishing; scroll for more.
4. `chat_url`: from the address bar.
5. `model_ui`: usually hidden when signed out; write `not shown (signed-out default)`.
6. `web_search`: `true` if the reply shows sources, citations or shopping cards.

## Claude

**Session:** signed in (set by the human) + Claude **Incognito chat toggle** on. New Incognito chat every prompt.

**Send**
1. Open `https://claude.ai`. Confirm you're signed in.
2. Start a new chat and **turn on the Incognito toggle**. Confirm the Incognito indicator shows before typing.
3. Paste the turn-1 text and press **Send**.
4. Wait until finished (1.1). Claude may show "Searched the web" or "Finding…" while working; that's not the end.
5. Multi-turn: send `followup_text` in the **same Incognito chat**.

**Save**
1. `answer.txt`: click **Copy** under the reply and paste. If Copy doesn't work, use the reply element's `innerText` only (no sidebar, prompt or status lines).
2. `answer.html`: save the reply DOM. If not possible, wrap the text in `<pre>` and set `capture_quality=text_wrapped_html`.
3. Screenshots: `shot_1.png` after finishing; scroll for more.
4. `chat_url`: Incognito chats usually have no lasting URL. Write `null` and note "Claude Incognito chat, no persistent URL".
5. `web_search`: `true` if "Searched the web" (or sources) appeared.
6. `model_ui`: the model name shown in the chat.

**Clarifying widget** (common on gift prompts) instead of a full answer: save what's visible, set `capture_quality=partial`, don't answer the widget unless the human asked you to.

## Gemini

**Session:** signed out (Incognito or shared profile). New chat every prompt.

**Send**
1. Open `https://gemini.google.com`. Confirm you're signed out (a "Sign in" button is visible).
2. Click **New chat**.
3. Paste the turn-1 text and press **Send**.
4. Wait until finished (1.1). Gemini can pause mid-answer; confirm the stop control is gone and the action bar is showing.
5. Multi-turn: send `followup_text` in the same chat.

**Save** (citations are fragile, so HTML comes first)
1. `answer.html` **first**: save the reply DOM or full page HTML. The Copy button alone drops citation chips. If the chips have no links in the HTML, note "citation chips name-only" in `notes`.
2. `answer.txt`: the reply's `innerText`. Chip labels may appear as plain source names without URLs; that's expected.
3. Optional: hover each citation chip and record any title or site shown, in `notes`.
4. Screenshots: `shot_1.png` after finishing. If a screenshot was taken mid-answer, take it again. If you can't, set `capture_quality=low` and say why.
5. `chat_url`: the `https://gemini.google.com/app/…` URL.
6. `model_ui`: whatever the app shows (signed-out Gemini often runs a lighter model, for example Flash-Lite).
7. `web_search`: `true` if source chips or citations appear.
