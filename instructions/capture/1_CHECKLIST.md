# Capture Checklist

capture/1_CHECKLIST v2.1 · 2026-10-27

Read this when your task is **Capture**. It's the order of work from first message to hand-off. Details live in two other files:

- `2_RUNBOOK.md`: policy, sessions, egress, parallel bots, failures
- `3_APP_GUIDE.md`: what to click and what to save in each app

Names (`run_id`, `run_key`, raw folder name and path) are defined in `README.md`.

Your job is to capture answers only. You do not build, load or touch any CSV.

---

## A. Before you start: get these from the human

Do not send any prompt until every item below is answered in the chat.

- [ ] **Apps**: ChatGPT, Claude and/or Gemini, and which bot does which.
- [ ] **Mode**:
  - **Delta**: the exact prompt IDs, or a `prompts_delta_*.csv` the human supplied, or prompt text the human pasted.
  - **Full**: every row with `active=1`. Needs an explicit "yes, full run".
- [ ] **run_id**: use the one the human gives. If none is given, propose one in the README format and get a yes. Every bot in the same run uses the same `run_id`.
- [ ] Confirm IDs are **`prompt_id` values only** (e.g. `CH03`). Do not put bot name or date into `prompt_id` or `run_key`; date/batch is `run_id`.
- [ ] **Session** for your app is ready. The human sets sign-in state; you never ask for or enter credentials.
  - **ChatGPT / Gemini:** **signed out**. Either a Chrome Incognito window or the signed-out shared profile is fine; no approval needed. Record which one you used in `meta.json` (`incognito` or `signed_out_shared_profile`).
  - **Claude:** signed in (already done by the human), with Claude's own **Incognito chat toggle** turned on for every prompt. A Chrome Incognito window does not replace the toggle.
- [ ] **Egress**: check the IP inside the capture browser. If the country is not US, ask whether to turn on Route traffic/VPN or proceed tagged `egress_country=IN`.

If the human asks for "N prompts" without giving IDs or rows: stop and ask. Never write prompts yourself.

## B. Set up

- [ ] Load prompts from `inputs/prompts_v3_final.csv` (skip `active=0`) or the supplied delta file.
- [ ] Confirm every requested ID exists. If any is missing, list them and ask.
- [ ] Open the session for your app as in A (ChatGPT/Gemini: confirm you are signed out; Claude: confirm signed in, then turn on the Incognito chat toggle).
- [ ] Create `runs/<run_id>/raw/<app>/` and record your start time (UTC).

## C. For each prompt

- [ ] Open a **new chat** (Claude: new Incognito chat).
- [ ] **Turn 1:** send `prompt_text` + one space + exactly `I'm shopping in the USA.`
  Example: `Where can I buy fine jewelry online? I'm shopping in the USA.`
- [ ] Wait until the answer has **completely finished**.
- [ ] Save the 4 files into the raw folder for `t1` (App Guide, your app's section).
- [ ] **Turn 2** (only if `followup_text` is not empty): send `followup_text` exactly as written, **no suffix**, in the **same chat**. Wait, then save into a separate raw folder for `t2`.

## D. After the last prompt

- [ ] Write `SUMMARY_<app>.md` and `run_info_<app>.json` in `runs/<run_id>/` (contents: App Guide, "Run files").
- [ ] Upload every raw folder **expanded** to `runs/<run_id>/raw/<app>/<raw folder>/` (one Drive folder per raw folder, files inside) plus both run files under `runs/<run_id>/`. A `raw_<app>.tar.gz` is an optional backup only; a tar alone is **not done**.
- [ ] List `runs/<run_id>/raw/<app>/` on Drive and check the folder count matches your local raw folders.
- [ ] Report to the human: Drive link, IDs captured, IDs failed with reasons, egress used, session used.
- [ ] **Stop.** Do not build CSVs unless the human asks.

---

## Stop and ask the human when

- ChatGPT **silent send-fail**: the prompt was sent but no chat was created. Stop that app at once (Runbook, "Failures").
- The browser IP is **not US** and the human hasn't approved IN.
- A requested prompt ID **doesn't exist** in the inputs.
- ChatGPT or Gemini **is signed in** and you can't get to a signed-out session.
- The app shows a **captcha or bot check** you can't pass.
- Two instructions **conflict**.

You don't need to ask for a **contaminated answer** (sent into the wrong chat or tab). Rename that raw folder to `__discarded_1`, re-run the ID in a fresh chat, and note it in SUMMARY (Runbook, "Failures").

## Never

- Invent prompt IDs, prompt text or follow-up text.
- Start a full run without an explicit yes.
- Edit or delete a raw file after writing it. (The only allowed change is renaming a bad folder to `__discarded_N`.)
- Write a summary or paraphrase into `answer.txt`.
- Record `incognito` when the shared profile was used.
- Record US egress when the browser IP was not US.
- Write files into another app's or another run's folder.
- Touch `inputs/` (except approved prompt additions) or `live_csv/`.
- Abort a run the human already approved for IN egress just because the user's computer went offline.
- Unpause the Claude "Resume" routine.
