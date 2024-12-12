#!/usr/bin/env python3
"""
Real-time Speech-to-Text Dictation Tool

This script provides real-time speech-to-text dictation functionality using either
local Whisper models or remote transcription services. It captures audio while a
designated key is held down and automatically types the transcribed text.

Usage:
    python dictation.py local [language] [options]
    python dictation.py remote [language] [options]
"""

import argparse
import subprocess
import threading
import time
import numpy as np
import pynput
import sounddevice as sd

# Default recording key (can be modified)
rec_key = pynput.keyboard.Key.ctrl_r

# Audio configuration
WHISPER_SAMPLERATE = 16000  # Whisper's required sampling rate
RECORDING_SAMPLERATE = 48000  # Input sampling rate (must be multiple of WHISPER_SAMPLERATE)
MIN_RECORDING_DURATION = 0.1  # Minimum recording duration in seconds

# Initialize keyboard controller
controller = pynput.keyboard.Controller()

# Command line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("engine", choices=["local", "remote"])
parser.add_argument("language", nargs="?", default=None)
parser.add_argument("--no-type-using-clipboard", action="store_true")
parser.add_argument("--on-callback", type=str, default=None)
parser.add_argument("--auto-off-time", type=int, default=None)
parser.add_argument("--model", type=str, default="whisper-1")
parser.add_argument("--use-oai", action="store_true", help="Use OpenAI API")
parser.add_argument("--use-groq", action="store_true", help="Use Groq API")
args = parser.parse_args()

# %% local or remote
if args.engine == "local":
    from faster_whisper import WhisperModel
    #model_size = "tiny.en"
    model_size = "small.en"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    #model = WhisperModel(args.model, device="cuda", compute_type="float16")
elif args.engine == "remote":
    from remote_transcription import get_text_remote
else:
    raise ValueError("Specify whether to use local or remote engine")

if args.on_callback is not None:
    subprocess.run(args.on_callback, shell=True)


# %%
def get_text_local(audio, context=None):
    """
    Transcribe audio using local Whisper model.
    
    Args:
        audio (numpy.ndarray): Audio data to transcribe
        context (str, optional): Previous context for improved transcription
        
    Returns:
        str: Transcribed text
    """
    segments, _ = model.transcribe(
        audio, 
        beam_size=5, 
        language=args.language, 
        initial_prompt=context
    )
    segments = list(segments)
    text = " ".join([segment.text.strip() for segment in segments])
    return text

def type_using_clipboard(text):
    """
    Type text directly using pynput keyboard controller.
    
    Args:
        text (str): Text to type
    """
    for char in text:
        controller.press(char)
        controller.release(char)
        time.sleep(0.001)  # Small delay to prevent characters from being missed


# %%
rec_key_pressed = False
time_last_used = time.time()


def record_and_process():
    """
    Record audio while the recording key is pressed and process it for transcription.
    Handles the complete pipeline of recording, processing, and text output.
    """
    audio_chunks = []

    def audio_callback(indata, frames, time, status):
        """Callback function for audio stream to collect audio chunks."""
        if status:
            print("WARNING:", status)
        audio_chunks.append(indata.copy())

    # Initialize audio input stream
    stream = sd.InputStream(
        samplerate=RECORDING_SAMPLERATE,
        channels=1,
        blocksize=256,
        callback=audio_callback,
    )
    stream.start()
    while rec_key_pressed:
        time.sleep(0.005)
    stream.stop()
    stream.close()
    recorded_audio = np.concatenate(audio_chunks)[:, 0]

    # Validate recording duration
    duration = len(recorded_audio) / RECORDING_SAMPLERATE
    if duration <= MIN_RECORDING_DURATION:
        print("Recording too short, skipping")
        return

    # Downsample audio to match Whisper's required sample rate
    # Using simple numpy downsampling for speed (every 3rd sample)
    recorded_audio = recorded_audio[::3]
    
    # Context handling (currently disabled)
    context = None

    # ! transcribe
    if args.engine == "local":
        text = get_text_local(recorded_audio, context)
    elif args.engine == "remote":
        text = get_text_remote(recorded_audio, args.language, context, args.use_groq)
    print(text)

    # ! type that text
    text = text + " "
    if not args.no_type_using_clipboard:
        #copy_to_clipboard(text)
        type_using_clipboard(text)
        #print("no_type_using_clipboard")
    else:
        #copy_to_clipboard(text)
        controller.type(text)
        # subprocess.run(["ydotool", "type", "--key-delay=0", "--key-hold=0", text])
        # note: ydotool on x11 correctly outputs polish chars and types in terminal


def on_press(key):
    """
    Handle key press events.
    Starts recording when the designated recording key is pressed.
    
    Args:
        key: The key that was pressed
    """
    global rec_key_pressed
    if key == rec_key:
        rec_key_pressed = True
        # Start recording in a separate thread
        threading.Thread(target=record_and_process).start()

def on_release(key):
    """
    Handle key release events.
    Stops recording when the recording key is released.
    
    Args:
        key: The key that was released
    """
    global rec_key_pressed, time_last_used
    if key == rec_key:
        rec_key_pressed = False
        time_last_used = time.time()


# %%
if args.language is not None:
    print(f"Using language: {args.language}")
with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print(f"Press {rec_key} to start recording")
    try:
        # listener.join()
        while listener.is_alive():
            #print('listener on')
            if args.auto_off_time is not None and time.time() - time_last_used > args.auto_off_time:
                print("Auto off")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")

