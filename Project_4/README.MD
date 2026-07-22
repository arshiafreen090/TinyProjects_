# WhatsApp AI Auto-Reply Bot 😸

An AI-powered WhatsApp bot that monitors a specific chat, detects incoming messages, and automatically replies using a large language model — all through desktop automation.

---

## Features

### Automated Chat Opening
- Clicks the WhatsApp taskbar icon to launch the app.
- Clicks the search bar, types the target contact name, and opens the chat — no manual steps required at startup.

### Screenshot-Based Change Detection
- Instead of continuously copying the full chat, the bot takes a small screenshot of only the latest-message area every 2 seconds and computes a hash of it.
- If the hash matches the previous one, nothing happened — the bot skips the cycle instantly with near-zero CPU usage.

### Typing Indicator Filter
- When a change is detected, the bot does **not** reply immediately.
- It waits until the watched region stays visually identical for 2 consecutive seconds (`STABLE_FOR`), confirming the person has finished typing and the full message has settled.
- This prevents the bot from reading and replying to a half-typed message or a "typing…" animation frame.

### Reliable Chat Copy with Auto-Retry
- Once a message is settled, the bot scrolls the chat to the bottom, then performs an explicit mouse-down → drag → mouse-up selection across the full chat area and copies it.
- If the clipboard comes back empty (can happen when the chat shifted during the drag), it retries up to 3 times before giving up.
- Only the **last line** of the copied text is extracted and used as the new message, so the bot doesn't re-process older messages.

### In-Memory Conversation History
- The bot maintains a `history` list in memory — a running log of user messages and AI replies in `{"role": ..., "content": ...}` format.
- Every time it replies, both the user's message and the AI's response are appended to this list.
- The full history is sent to the AI on every reply, so the model always has full context without needing to re-copy the chat.

### Duplicate Reply Prevention
- After sending a reply, the bot waits for it to appear in the chat, then re-baselines the screenshot hash.
- This means the layout shift caused by the bot's own sent message is captured as the new normal, preventing it from being detected as a new incoming message.
- A `last_processed_message` variable also ensures the same message text is never replied to twice.

### Idle Timeout and Auto-Exit
- If the watched region stays unchanged for 30 seconds after the last reply, the bot presses Escape to exit the chat and stops cleanly.

### AI Persona via OpenRouter
- The bot uses `nvidia/nemotron-3-nano-30b-a3b:free` (served through OpenRouter) with a custom system prompt.
- The persona is "Afreeeenz" — a 21-year-old developer from India who chats naturally in English and Hinglish, keeps replies short and conversational, and never reveals it is an AI.
- The model is swappable — change `MODEL` in `client.py`.

### Logging
- All activity (new messages, replies, warnings, errors) is written to both the terminal and `bot.log` for easy debugging.

---

## File Structure

```
Project_4/
├── bot.py            # Main automation loop and UI control
├── client.py         # OpenRouter/OpenAI client, persona, generate_reply()
├── utils.py          # Logging setup and wait_until() helper
├── get_cursor.py     # Utility to print live mouse coordinates (for tuning)
├── requirements.txt  # Python dependencies
└── .env              # API key (not committed)
```

---

## Setup

1. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** in `Project_4/` with your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_key_here
   ```

3. **Tune coordinates** to match your screen resolution.  
   Run `python get_cursor.py`, hover over each element, and update the constants at the top of `bot.py`:

   | Constant | Purpose |
   |---|---|
   | `WHATSAPP_ICON` | WhatsApp in the taskbar |
   | `SEARCH_BAR` | Contact search box |
   | `TEXT_BOX` | Message input field |
   | `SEND_BUTTON` | Send button |
   | `COPY_START / COPY_END` | Top-left and bottom-right of the chat area to select |
   | `LATEST_MSG_REGION` | `(left, top, width, height)` strip around the last message |

4. **Set the target contact** — change `TARGET_NAME` in `bot.py` to the exact name as it appears in WhatsApp.

5. **Run the bot**
   ```
   python bot.py
   ```

---

## Fallbacks and Limitations😶‍🌫️

| Situation | What happens |
|---|---|
| Copy returns empty (chat scrolled during drag) | Retries up to 3 times before skipping |
| Model returns no reply (rate limit / API error) | Logs a warning with the error detail; skips that cycle without crashing |
| "Typing…" animation fires change detection early | `wait_for_settled_message()` keeps waiting until the region is stable for 2s |
| Bot's own sent message re-triggers detection | Re-baselined after sending; `last_processed_message` check also guards it |
| Window moved or resolution changed | All pixel coordinates break — re-run `get_cursor.py` and update constants |
| Target chat not found during search | Bot opens WhatsApp and search but may land on wrong chat — no verification step yet |
| Very long typing session | `STABLE_TIMEOUT = 60s` cap kicks in and reads whatever is settled at that point |
| WhatsApp is minimized or behind another window | Screenshot-based detection will read the wrong content — WhatsApp must be visible |

---

## Configuration Reference

| Constant | Default | Description |
|---|---|---|
| `POLL_INTERVAL` | `2` s | How often to screenshot and check for changes |
| `STABLE_FOR` | `2.0` s | How long the region must be unchanged to count as a full message |
| `STABLE_TIMEOUT` | `60.0` s | Max time to wait for a message to settle |
| `IDLE_TIMEOUT` | `30` s | Inactivity time before exiting the chat |

---

> 🌱**Note:** This is a small, growing, and learning-phase project. It started as a basic pixel-polling bot and is progressively evolving — better change detection, smarter copy logic, in-memory context, and typing-filter have already been added. Future iterations will improve reliability, add multi-contact support, handle missed messages on startup, and reduce dependency on fixed screen coordinates. Progress will continue.
