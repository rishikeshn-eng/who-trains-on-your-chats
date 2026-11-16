# who-trains-on-your-chats

Most people don't know whether their chatbot conversations are used to train AI, or where the off switch is. This page answers that for eight popular chatbots, using each company's own words.

**Live: https://rishikeshn-eng.github.io/who-trains-on-your-chats/**

## What it showed on 16 November 2026

- All 8 apps say they may use personal-account chats to train their AI.
- 6 describe a way to turn that off: ChatGPT, Claude, Gemini, Copilot, Grok and Le Chat.
- For DeepSeek and Perplexity, the policy pages read here describe no off switch.
- Meta AI is missing, because Meta's privacy pages refuse automated reading.

## How it works

1. `providers.json` holds the answers. Each answer has a plain summary and the exact sentence from the company's policy that supports it.
2. `scripts/check.py` re-reads every policy page each day and checks that each quoted sentence is still there, word for word.
3. If a sentence is gone, the page marks that entry in red and logs the change, so a stale claim can't sit there unnoticed.
4. A GitHub Action runs the check every morning and republishes the page.

## Run it

```bash
pip install requests trafilatura
python scripts/check.py
```

Then serve the `docs` folder with any static file server.

## Limits

- A policy says what a company may do. This can't see what any company actually does.
- The short summaries are my reading of each quote. The exact words are on the page next to each one.
- Personal accounts only. Work, school and developer accounts usually have different rules.
- Rules can differ by country. These are the English pages as served to one location.
- It is information, and it isn't legal advice.

Built by Rishikesh Nair.
