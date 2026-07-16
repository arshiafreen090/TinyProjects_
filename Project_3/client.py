import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file (if present)
load_dotenv()

# Read OpenRouter API key from environment
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY not found. Create a .env file with OPENROUTER_API_KEY=sk-or-v1-..."
    )

# Initialize OpenAI client pointing to OpenRouter
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

def main():
    try:
        completion = client.chat.completions.create(
            model="nvidia/nemotron-3-nano-30b-a3b:free",
            messages=[
                {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud"},
                {"role": "user", "content": "what is coding"}
            ]
        )
        print(completion.choices[0].message.content)
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()