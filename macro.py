"""
Macro Recorder GUI using PySimpleGUI.

This program allows users to:
- Record mouse clicks and keyboard key presses.
- Save and load recorded macros to/from a file.
- Replay recorded events using PyAutoGUI.

Author: Mihailo Hranisavljevic  
Version: March 22, 2025
"""

import PySimpleGUI as sg
import pyautogui
import time
from pynput import mouse, keyboard
import threading
import pickle

# Stores recorded events
events = []

# Indicates whether recording is active
recording = False

def record_mouse():
    """
    Records mouse click events while recording is active.
    Appends events as tuples to the global `events` list.
    """
    def on_click(x, y, button, pressed):
        if recording:
            events.append(('mouse_click', time.time(), x, y, button.name, pressed))

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

def record_keyboard():
    """
    Records keyboard press events while recording is active.
    Appends events as tuples to the global `events` list.
    """
    def on_press(key):
        if recording:
            try:
                events.append(('key_press', time.time(), key.char))
            except AttributeError:
                events.append(('key_press', time.time(), str(key)))

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def play_events(start_time):
    """
    Plays back the recorded events, reproducing mouse clicks and key presses.

    Args:
        start_time (float): Timestamp of the first event to sync playback delay.
    """
    for event in events:
        event_type, t, *args = event
        time.sleep(t - start_time)
        if event_type == 'mouse_click':
            _, _, x, y, button, pressed = event
            pyautogui.click(x, y)
        elif event_type == 'key_press':
            _, _, key = event
            pyautogui.press(key)

# GUI layout
layout = [
    [sg.Text("Macro Recorder", font=("Helvetica", 16))],
    [sg.Button("Start Recording"), sg.Button("Stop Recording"), sg.Button("Play Macro")],
    [sg.Button("Save Macro"), sg.Button("Load Macro")],
    [sg.Output(size=(60, 10))]
]

window = sg.Window("Python Macro Recorder", layout)

mouse_thread = None
keyboard_thread = None
start_time = None

while True:
    event, values = window.read(timeout=100)

    if event == sg.WINDOW_CLOSED:
        break

    if event == "Start Recording":
        events.clear()
        recording = True
        start_time = time.time()
        print("[*] Recording started...")
        mouse_thread = threading.Thread(target=record_mouse, daemon=True)
        keyboard_thread = threading.Thread(target=record_keyboard, daemon=True)
        mouse_thread.start()
        keyboard_thread.start()

    elif event == "Stop Recording":
        recording = False
        print("[*] Recording stopped.")

    elif event == "Play Macro":
        if events:
            print("[*] Playing back...")
            base_time = events[0][1]
            play_events(base_time)
        else:
            print("[!] No events recorded.")

    elif event == "Save Macro":
        filename = sg.popup_get_file("Save as", save_as=True, file_types=(("Macro Files", "*.macro"),))
        if filename:
            with open(filename, 'wb') as f:
                pickle.dump(events, f)
                print(f"[*] Macro saved to {filename}")

    elif event == "Load Macro":
        filename = sg.popup_get_file("Load Macro", file_types=(("Macro Files", "*.macro"),))
        if filename:
            with open(filename, 'rb') as f:
                events = pickle.load(f)
                print(f"[*] Macro loaded from {filename}")

window.close()
