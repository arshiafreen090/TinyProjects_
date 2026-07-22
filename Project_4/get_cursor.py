"""Utility: print the current mouse position.

Useful for finding the coordinates to configure in bot.py. Press Ctrl+C to
stop.
"""
import time

import pyautogui


def main() -> None:
    print("Move the mouse to read its position. Press Ctrl+C to stop.")
    try:
        while True:
            print(pyautogui.position())
            time.sleep(0.5)  # avoid pegging the CPU at 100%
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
