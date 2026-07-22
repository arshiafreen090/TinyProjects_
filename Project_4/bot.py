import hashlib
import time

import pyautogui
import pyperclip

from client import generate_reply
from utils import setup_logging, wait_until

log = setup_logging()

# The contact to open and reply to.
TARGET_NAME = "Aaquib Bhai"

# ---- Hardcoded pixel locations ----
WHATSAPP_ICON = (1372, 1167)   # taskbar/app icon to open WhatsApp
SEARCH_BAR = (215, 219)        # search box to find the contact
TEXT_BOX = (789, 1091)         # message input box
SEND_BUTTON = (1875, 1085)     # send button

# Chat content region to drag-select and copy: top-left -> bottom-right.
COPY_START = (708, 217)
COPY_END = (1516, 1046)

# Region of the latest-message area to watch for changes, as
# (left, top, width, height). Only this small strip is screenshotted each
# poll instead of copying the whole chat.
LATEST_MSG_REGION = (708, 900, 808, 146)

# How often to check the latest-message area, in seconds.
POLL_INTERVAL = 2

# After a change is seen, the region must stay identical for this many
# seconds before it counts as a settled, fully-arrived message. This skips
# the "typing..." animation, which keeps changing while the person types.
STABLE_FOR = 2.0

# Safety cap on how long to wait for the message to settle (e.g. a very
# long message still being typed).
STABLE_TIMEOUT = 60.0

# How long to wait for a new message before exiting the chat.
IDLE_TIMEOUT = 30


def open_whatsapp() -> None:
    """Open WhatsApp from its coded icon location."""
    pyautogui.click(*WHATSAPP_ICON)
    time.sleep(2)


def open_chat(name: str) -> None:
    """Search for the contact and open the chat."""
    pyautogui.click(*SEARCH_BAR)
    time.sleep(0.5)
    pyperclip.copy(name)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(1)


def latest_msg_hash() -> str:
    """Hash a screenshot of the latest-message region to detect changes."""
    shot = pyautogui.screenshot(region=LATEST_MSG_REGION)
    return hashlib.sha256(shot.tobytes()).hexdigest()


def wait_for_settled_message() -> str:
    """Wait until the latest-message region stops changing, then return it.

    While the other person is typing, the region keeps changing (the
    "typing..." animation and the growing text). We only act once it has
    stayed identical for STABLE_FOR seconds, meaning the full message has
    arrived. Returns the settled hash.
    """
    deadline = time.monotonic() + STABLE_TIMEOUT
    current = latest_msg_hash()
    stable_since = time.monotonic()

    while time.monotonic() < deadline:
        time.sleep(0.5)
        new = latest_msg_hash()
        if new != current:
            # Still changing (typing / message growing); reset the timer.
            current = new
            stable_since = time.monotonic()
        elif time.monotonic() - stable_since >= STABLE_FOR:
            return current
    return current


def read_latest_message() -> str:
    """Scroll to the newest message, copy the chat, and return the last line.

    The drag-select can grab nothing if the chat is scrolled up or the
    selection doesn't register, so we first scroll to the bottom and then
    retry the select/copy a few times until the clipboard actually changes.
    """
    # Make sure we're at the very bottom so the newest message is in view.
    pyautogui.click(*COPY_END)
    pyautogui.scroll(-3000)
    time.sleep(0.4)

    for attempt in range(3):
        pyperclip.copy("")  # clear so we can detect a real copy
        # Explicit press/drag/release is more reliable than dragTo alone.
        pyautogui.moveTo(*COPY_START)
        pyautogui.mouseDown(button="left")
        pyautogui.moveTo(*COPY_END, duration=0.8)
        pyautogui.mouseUp(button="left")
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "c")

        if wait_until(lambda: pyperclip.paste().strip() != "", timeout=3):
            break
        log.warning("Copy attempt %d got nothing; retrying.", attempt + 1)

    text = pyperclip.paste()

    # Remove the highlight so it can't interfere with the next screenshot.
    pyautogui.click(*TEXT_BOX)
    time.sleep(0.3)

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def send_reply(text: str) -> None:
    """Paste the reply into the text box and click send."""
    pyperclip.copy(text)
    pyautogui.click(*TEXT_BOX)
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)
    pyautogui.click(*SEND_BUTTON)


def exit_chat() -> None:
    """Leave the current chat."""
    pyautogui.press("escape")


def main() -> None:
    log.info("Starting WhatsApp auto-reply bot for %r", TARGET_NAME)
    open_whatsapp()
    open_chat(TARGET_NAME)

    # In-memory conversation so the whole chat never has to be re-copied.
    history: list[dict[str, str]] = []
    last_processed_message = ""
    # Baseline of the latest-message area; only changes trigger a reply.
    baseline_hash = latest_msg_hash()
    last_activity = time.monotonic()

    while True:
        try:
            time.sleep(POLL_INTERVAL)

            # Cheap check: has the latest-message strip changed at all?
            if latest_msg_hash() == baseline_hash:
                if time.monotonic() - last_activity >= IDLE_TIMEOUT:
                    log.info("Idle for %ss; exiting chat.", IDLE_TIMEOUT)
                    exit_chat()
                    break
                continue

            # A change appeared (could be the "typing..." indicator). Wait
            # until it settles so we read the full message, not mid-typing.
            log.info("Change detected; waiting for message to settle...")
            wait_for_settled_message()

            # Read only the newest message once it has fully arrived.
            message = read_latest_message()
            if not message:
                # Copy failed entirely; don't re-baseline so the next loop
                # tries again instead of dropping the message.
                log.warning("Could not copy any text; will retry next poll.")
                continue
            if message == last_processed_message:
                # Same message we already handled (or our own reply echo).
                baseline_hash = latest_msg_hash()
                continue

            log.info("New message: %s", message)
            history.append({"role": "user", "content": message})
            last_processed_message = message

            reply = generate_reply(history)
            if reply.strip():
                send_reply(reply)
                history.append({"role": "assistant", "content": reply})
                log.info("Replied: %s", reply)
            else:
                log.warning("Model returned an empty reply.")

            # Re-baseline AFTER our reply lands so it isn't seen as a new
            # incoming message, and reset the idle timer.
            time.sleep(1)
            baseline_hash = latest_msg_hash()
            last_activity = time.monotonic()

        except KeyboardInterrupt:
            log.info("Stopped by user (KeyboardInterrupt).")
            break


if __name__ == "__main__":
    main()