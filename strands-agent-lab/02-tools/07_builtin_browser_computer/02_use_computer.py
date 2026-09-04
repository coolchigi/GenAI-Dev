# Built-in tool: use_computer — desktop GUI automation + OCR
# -----------------------------------------------------------
# `use_computer` controls the physical desktop: mouse, keyboard, screenshots,
# and OCR text extraction from screen regions. It can automate any GUI
# application visible on your screen.
#
# Capabilities:
#   mouse_move      — move cursor to (x, y) coordinates
#   mouse_click     — click at a position (left/right/double)
#   mouse_drag      — drag from one position to another
#   type_text       — type a string at the current cursor position
#   key_press       — press a keyboard shortcut (e.g. "cmd+c", "ctrl+z")
#   screenshot      — capture the full screen or a region
#   ocr_extract     — extract text from a screen region using OCR
#   app_open        — open an application by name
#   app_close       — close an application
#   app_list        — list running applications
#
# Platform notes:
#   - macOS: requires Quartz (installed with macOS, no extra install)
#   - macOS: Accessibility permissions required for mouse/keyboard control
#     (System Settings → Privacy & Security → Accessibility → add Terminal)
#   - Linux: requires X11 (works headless with Xvfb)
#   - Windows: uses win32api
#
# Prerequisites:
#   uv add pyautogui pytesseract opencv-python Pillow
#   brew install tesseract    # for OCR on macOS

from strands import Agent
from strands_tools import use_computer
from common import nova


agent = Agent(
    model=nova(0.0),
    system_prompt=(
        "You are a desktop assistant. Use the use_computer tool to interact "
        "with the desktop. You can take screenshots, read text from the screen, "
        "and control the mouse and keyboard. Always describe what you observe."
    ),
    tools=[use_computer],
)


if __name__ == "__main__":
    print("=== Take a screenshot and describe it ===")
    # This is the safest action — no mouse/keyboard movement.
    agent(
        "Take a screenshot of the full screen and describe what you see. "
        "What applications appear to be open?"
    )

    print("\n=== OCR: read text from the screen ===")
    # Extracts text from the top-left corner of the screen (menu bar area on macOS).
    agent(
        "Use OCR to extract and read the text visible in the top-left region "
        "of the screen (approximately x=0, y=0, width=400, height=30)."
    )

    # ── Mouse control examples (uncomment to try) ────────────────────────
    # These move the mouse — make sure your screen is in a safe state first.
    # agent("Move the mouse cursor to the centre of the screen.")
    # agent("Press Command+Space to open Spotlight search on macOS.")


# ── How to run ────────────────────────────────────────────────────────────
# macOS only for the full feature set. AWS credentials required for the model.
#
# One-time setup:
#     uv add pyautogui pytesseract opencv-python Pillow
#     brew install tesseract
#
# Grant accessibility permissions (macOS):
#   System Settings → Privacy & Security → Accessibility
#   → Add your terminal application (Terminal, iTerm2, etc.)
#
# Run:
#     aws-vault exec strands-lab -- uv run 02-tools/07_builtin_browser_computer/02_use_computer.py
#
# The screenshot and OCR actions work without accessibility permissions.
# Mouse/keyboard control requires the permissions above.
