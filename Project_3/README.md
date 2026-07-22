# Jarvis Voice Assistant🤖 

A Python voice assistant that listens for spoken commands and can open websites, play music, fetch news, and answer general questions via an AI model.

## Features

- **Speech recognition** — records audio via `sounddevice`, transcribes via Google's speech API (`speech_recognition`).
- **Text-to-speech** — responses spoken aloud via `pyttsx3`.
- **Browser commands** — "open google", "open facebook", "open youtube", "open linkedin".
- **Music playback** — "play <song name>", looked up from `musicLib.py`.
- **News headlines** — say "news" to fetch and read out the latest India headlines via NewsAPI.
- **AI chat fallback** — anything that doesn't match a known command is sent to an AI model (via OpenRouter) and the reply is spoken.
- **Session timeout** — if Jarvis hears nothing for 30 consecutive seconds, it says "Exiting the current session." and closes.

## Requirements

- Python 3.10+
- [FLAC](https://xiph.org/flac/) command-line tool installed and available on your system `PATH` (required by `speech_recognition` to encode audio for Google's API)
- A working microphone

### Python packages

```
pip install SpeechRecognition pyttsx3 sounddevice scipy requests openai python-dotenv
```

## Setup

1. **Install FLAC** and confirm it's on PATH (especially important on ARM64 laptops — see the "Known limitations" note below about `speech_recognition`'s ARM64 fallback gap):
   ```
   flac --version
   ```

2. **Create a `.env` file** in the project root with your API keys:
   ```
   NEWS_API_KEY=your_newsapi_key_here
   OPENROUTER_API_KEY=your_openrouter_key_here
   ```
   - Get a NewsAPI key from [newsapi.org](https://newsapi.org)
   - Get an OpenRouter key from [openrouter.ai](https://openrouter.ai)

3. **Create `musicLib.py`** in the project root with your song library:
   ```python
   music = {
       "perfect": "https://www.youtube.com/watch?v=...",
       "shape of you": "https://www.youtube.com/watch?v=...",
   }
   ```

4. **Run it:**
   ```
   python main.py
   ```

## Usage

Once running, Jarvis speaks an intro and starts listening in 5-second chunks. Speak a command such as:

- "open youtube"
- "play perfect"
- "news"
- "what's the weather like generally in monsoon season" *(falls through to AI chat)*

If Jarvis doesn't hear anything for 30 seconds straight (six silent 5-second listening rounds), it automatically ends the session.

## Known limitations😶‍🌫️

- Recording is a fixed 5-second window per listen cycle — it isn't silence-aware, so it always records the full 5 seconds even if you finish speaking sooner, and can cut off longer sentences.
- Google's free speech recognition endpoint (`recognize_google`) is unofficial and rate-limited — not meant for heavy or production use.
- NewsAPI's free tier has usage restrictions; check their docs if requests start failing.
- ARM-based Windows machines may need the FLAC path pinned manually (see the `FLAC_PATH` workaround at the top of `main.py`) since `speech_recognition`'s bundled-binary fallback doesn't cover ARM64.

## Project structure

```
.
├── main.py          # entry point — listening loop, command routing, TTS
├── musicLib.py       # song name -> link mapping (create this yourself)
├── .env              # API keys (not committed to version control)
└── README.md
```

## 🌱Note

```
This is a very small, beginner-level implementation of an AI assistant.
It's missing a lot — proper wake-word detection, silence-aware recording,
error handling, conversation memory, and more. But building it end-to-end
was genuinely useful for learning the foundations: speech recognition,
text-to-speech, API integration, and tying it all together into a working
loop. If you're learning too, building something like this yourself is
well worth trying, lets goo... (*^_^*)
```