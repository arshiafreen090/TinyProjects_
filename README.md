# Python Projects

This is my personal Python learning space. Every project here represents a step forward — from basic logic and terminal games to working APIs, voice assistants, and AI-powered automation. Each one was built to learn something new, not just to finish something.

---

## Project 1 — Snake, Gun, Water

A terminal-based Snake-Gun-Water game (the Indian version of Rock-Paper-Scissors).

- Random computer choice, player inputs a letter (`s`, `w`, `g`).
- Win/lose/tie logic handled with dictionaries instead of long if-else chains.
- Simple and intentional — written to understand basic Python flow before anything else.

---

## Project 2 — The Perfect Guess

A number guessing game where the computer picks a random number between 1–100 and the player guesses until they get it right.

- Tracks the number of attempts.
- Gives higher/lower hints each guess.
- First real use of `while` loops and user input validation.

---

## Project 3 — Jarvis Voice Assistant

A voice-controlled assistant that listens, speaks back, and can do useful things.

- Speech-to-text via Google's API, text-to-speech via `pyttsx3`.
- Opens websites, plays music from a local library, reads live news headlines.
- Falls back to an AI model (via OpenRouter) for anything it doesn't recognise.
- Auto-exits after 30 seconds of silence.

First project involving real APIs, audio I/O, and a proper multi-file structure.

---

## Project 4 — WhatsApp AI Auto-Reply Bot

A desktop automation bot that monitors a WhatsApp chat and replies using an AI persona.

- Uses PyAutoGUI to open WhatsApp, search for a contact, and control the chat window — all via hardcoded pixel coordinates.
- Screenshots only the latest-message area every 2 seconds to detect changes cheaply.
- Waits for the "typing…" animation to stop before reading and replying, so it never catches a half-typed message.
- Retries the copy up to 3 times if the chat shifts during selection.
- Keeps an in-memory conversation history so the AI always has full context.
- Auto-exits the chat after 30 seconds of inactivity.

Most complex project so far — combines automation, vision, AI, and session management.

---

> These projects are a record of progression, not a polished portfolio. They will keep evolving.
