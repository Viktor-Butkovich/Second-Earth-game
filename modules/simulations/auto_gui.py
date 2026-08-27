import pyautogui
import sys
import subprocess
from scmrepo.git import Git
import pygetwindow as gw
import time
from pathlib import Path
from pynput.keyboard import Controller, Key

PACKAGE_ROOT = Git(root_dir=".").root_dir
kb = Controller()
pipe_path = Path(f"{PACKAGE_ROOT}/Outputs/AutoGUI/autogui_pipe.txt")
if pipe_path.exists():
    pipe_path.unlink()  # Remove existing pipe file
pipe_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
pipe_path.touch()  # Create the pipe file


def press(key: str) -> None:
    kb.press(key)
    time.sleep(0.05)
    kb.release(key)
    time.sleep(0.05)


def get_exact_window(title) -> gw.Win32Window:
    candidates = gw.getWindowsWithTitle(title)
    for win in candidates:
        if win.title == title:
            return win
    return None


def wait_for_window(title, timeout=30) -> gw.Win32Window:
    start = time.time()
    while time.time() - start < timeout:
        window = get_exact_window(title)
        if window:
            return window
        time.sleep(0.05)
    raise Exception(f"Wait for window {title} timed out after {timeout} seconds.")


def await_signal(message: str, process: subprocess.Popen = None) -> None:
    """Reads lines from the pipe. Exits automatically if the game process terminates."""
    with open(pipe_path, "r") as fifo:
        while True:
            # Check if the process crashed while waiting
            if process and process.poll() is not None:
                raise RuntimeError("Game process exited")

            line = fifo.readline().strip()
            if line == message:
                break

            time.sleep(0.05)  # Avoid busy-waiting

    pipe_path.write_text("")
    time.sleep(0.05)


def start_game_thread() -> subprocess.Popen:
    process = subprocess.Popen([sys.executable, f"{PACKAGE_ROOT}/main.py"])
    return process


def load_and_select_first_unit():
    game_process = start_game_thread()
    window = wait_for_window("SE")
    window.activate()
    await_signal("loading", game_process)
    await_signal("loaded", game_process)
    press("l")
    await_signal("loading", game_process)
    await_signal("loaded", game_process)
    press(Key.enter)
    press(Key.tab)
    while game_process.poll() is None:
        time.sleep(0.1)


def new_game():
    game_process = start_game_thread()
    window = wait_for_window("SE")
    window.activate()
    await_signal("loading", game_process)
    await_signal("loaded", game_process)
    press("n")
    time.sleep(0.05)
    press("n")
    await_signal("loading", game_process)
    await_signal("loaded", game_process)
    press(Key.enter)
    while game_process.poll() is None:
        time.sleep(0.1)
