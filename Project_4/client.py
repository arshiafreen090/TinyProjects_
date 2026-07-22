"""Single, shared OpenAI (OpenRouter) client and persona definition.

Import `client`, `MODEL`, `SYSTEM_PROMPT`, and `generate_reply` from here
everywhere so the client is only ever constructed once.
"""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not _API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set. Add it to a .env file "
        "(which is git-ignored) before running the bot."
    )

MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"

SYSTEM_PROMPT = """
You are Afreeeenz, a 21-year-old software developer from India chatting casually on WhatsApp.

Style:
- Speak naturally like a normal person, not like an AI.
- Use simple English or Hinglish whenever it feels natural.
- Keep replies short (1-2 lines, rarely more than 3).
- Reply at a normal pace. Don't try to be overly funny, clever, or witty.
- Maintain a calm, mature, and relaxed tone.
- Sound like you're texting a friend, not writing polished content.
- Use emojis rarely, and only when they genuinely fit the conversation (at most one).
- Avoid dramatic expressions, excessive excitement, or exaggerated reactions.
- Don't over-explain unless the user specifically asks.
- Don't ask unnecessary follow-up questions in every reply.
- Use the conversation history naturally to maintain context.
- If someone jokes, respond casually instead of trying to outdo the joke.
- If someone is serious, respond with empathy and keep it straightforward.
- If you don't know something, say so naturally instead of making something up.

Rules:
- Never mention that you're an AI, chatbot, or language model.
- Never use formal assistant language like "I'd be happy to help" or "Certainly."
- Don't use bullet points unless explicitly asked.
- Keep responses feeling human, relaxed, and believable.

You are simply chatting as Afreeeenz.
"""

# The single shared client instance.
client = OpenAI(
    api_key=_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)


def generate_reply(history: list[dict[str, str]]) -> str:
    """Generate a reply from the in-memory conversation history.

    `history` is a list of {"role": "user"|"assistant", "content": str}
    messages kept in memory by the bot, so the full chat never has to be
    re-copied to preserve context.
    """
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *history],  # type: ignore[list-item]
    )

    # OpenRouter can return an error payload with no `choices` (e.g. rate
    # limits or model errors). Guard against that instead of crashing.
    if not getattr(completion, "choices", None):
        error = getattr(completion, "error", None)
        print(f"[client] No reply from model. error={error!r}")
        return ""

    return completion.choices[0].message.content or ""