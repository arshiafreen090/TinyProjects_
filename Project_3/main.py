import os
import sys          # needed for sys.exit() on timeout
import shutil
import webbrowser
import speech_recognition as sr
import pyttsx3
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import musicLib as musicLibrary
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()



# --- Root-cause fix: hard-pin flac so speech_recognition never has to guess ---
FLAC_PATH = shutil.which("flac")  # or hardcode e.g. r"C:\ProgramData\chocolatey\bin\flac.exe"
if FLAC_PATH is None:
    raise RuntimeError("flac.exe not found on PATH — check installation")

import speech_recognition.audio as sr_audio
sr_audio.get_flac_converter = lambda: FLAC_PATH  # bypass the broken machine-type detection
# -------------------------------------------------------------------------

recognizer = sr.Recognizer()
newsAPI = os.getenv("NEWS_API_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

MAX_SILENT_SECONDS = 30  # total allowed inactivity before auto-exit
LISTEN_DURATION = 5      # matches listen_audio()'s recording length


def listen_audio():
    fs = 16000
    duration = 5
    print("Listening...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()

    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_file.close()  # release the handle so Windows allows read/write access

    write(temp_file.name, fs, recording)

    with sr.AudioFile(temp_file.name) as source:
        audio = recognizer.record(source)

    os.remove(temp_file.name)
    return audio
def aiProcess(command):
    client = OpenAI(
        api_key=openrouter_key,
        base_url="https://openrouter.ai/api/v1"
    )

    completion = client.chat.completions.create(
        model="nvidia/nemotron-3-nano-30b-a3b:free",
        messages=[
            {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud. Give short responses please"},
            {"role": "user", "content": command}
        ]
    )

    return completion.choices[0].message.content


def speak(text):
    local_engine = pyttsx3.init()
    local_engine.say(str(text))
    local_engine.runAndWait()
    local_engine.stop()


def process_command(c):
    c_low = c.lower()
    if "open google" in c_low:
        speak("Opening Google...")
        webbrowser.open("https://www.google.com")
    elif "open facebook" in c_low:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c_low:
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c_low:
        webbrowser.open("https://linkedin.com")
    elif c_low.startswith("play"):
        try:
            song = c_low.replace("play", "", 1).strip()
            link = musicLibrary.music[song]
            webbrowser.open(link)
        except KeyError:
            speak(f"Sorry, I don't have {song} in my library.")
            print(f"Available songs: {', '.join(musicLibrary.music.keys())}")

    elif "news" in c_low:
        speak("Fetching today's news")
        try:
            r = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": "India",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "apiKey": newsAPI,
                },
                timeout=10,
            )
            print(f"[DEBUG] News API status: {r.status_code}")

            if r.status_code != 200:
                print(f"[DEBUG] News API error body: {r.text}")
                speak("Sorry, I couldn't fetch the news right now.")
                return

            data = r.json()
            articles = data.get("articles", [])

            if not articles:
                speak("No news articles found")
                return

            for i, article in enumerate(articles[:5], start=1):
                headline = article.get("title", "")
                print(f"Headline {i}: {headline}")
                speak(headline)

        except requests.RequestException as e:
            print(f"[DEBUG] News request failed: {e}")
            speak("Sorry, there was a problem reaching the news service.")
    else:
        #openAI will take the response >_<
       output = aiProcess(c)
       speak(output) 

        

if __name__ == "__main__":
    speak("Initializing Jarvis.... I am your personal assistant. How can I help you today Ma'am?")
    print("Initializing Jarvis.... I am your personal assistant. How can I help you today Ma'am?")
    silent_seconds = 0  # tracks consecutive seconds with no recognized speech
    while True:
        audio = listen_audio()
        print("Recognizing...")
        try:
            command = recognizer.recognize_google(audio)  # type: ignore[attr-defined]
            print(f"{command}\n")
            silent_seconds = 0  # reset timer since speech was heard

            # terminate only if the command is EXACTLY "stop" or "exit"
            # (not when those words appear inside a longer sentence)
            if command.strip().lower() in ("stop", "exit"):
                print("Exiting the current session.")
                speak("Exiting the current session.")
                sys.exit(0)

            process_command(command)
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            silent_seconds += LISTEN_DURATION  # no speech heard this round
        except sr.RequestError as e:
            print(f"Sorry, my speech service is down. {e}")
            silent_seconds += LISTEN_DURATION  # count this round too

        # 30-second inactivity timeout
        if silent_seconds >= MAX_SILENT_SECONDS:
            print("Exiting the current session.")
            speak("Exiting the current session.")
            sys.exit(0)