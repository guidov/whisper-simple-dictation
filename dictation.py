#!/usr/bin/env python3
"""
Real-time Speech-to-Text Dictation Tool

Usage:
    python dictation.py local [language]
    python dictation.py remote [language] [--use-groq]
"""

import argparse
import threading
import time
import numpy as np
import pynput
import sounddevice as sd
from clipboard_util import type_using_clipboard

# Default recording key
rec_key = pynput.keyboard.Key.ctrl_r

# Audio configuration
WHISPER_SAMPLERATE = 16000
RECORDING_SAMPLERATE = 48000
MIN_RECORDING_DURATION = 0.1

# Initialize keyboard controller
controller = pynput.keyboard.Controller()

# Command line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("engine", choices=["local", "remote"])
parser.add_argument("language", nargs="?", default=None)
parser.add_argument("--use-groq", action="store_true", help="Use Groq API")
args = parser.parse_args()

# Initialize transcription engine
if args.engine == "local":
    from faster_whisper import WhisperModel
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
elif args.engine == "remote":
    from remote_transcription import get_text_remote
else:
    raise ValueError("Specify whether to use local or remote engine")

def get_text_local(audio, context=None):
    """Transcribe audio using local Whisper model."""
    segments, _ = model.transcribe(
        audio, 
        beam_size=5, 
        language=args.language
    )
    segments = list(segments)
    return " ".join([segment.text.strip() for segment in segments])

rec_key_pressed = False

def record_and_process():
    """Record and transcribe audio while recording key is pressed."""
    audio_chunks = []

    def audio_callback(indata, frames, time, status):
        if status:
            print("WARNING:", status)
        audio_chunks.append(indata.copy())

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
    duration = len(recorded_audio) / RECORDING_SAMPLERATE
    
    if duration <= MIN_RECORDING_DURATION:
        print("Recording too short, skipping")
        return

    # Downsample audio
    recorded_audio = recorded_audio[::3]

    # Transcribe
    if args.engine == "local":
        text = get_text_local(recorded_audio)
    else:
        text = get_text_remote(recorded_audio, args.language, None, args.use_groq)
    
    print(text)
    type_using_clipboard(text + " ")

def on_press(key):
    """Start recording when designated key is pressed."""
    global rec_key_pressed
    if key == rec_key:
        rec_key_pressed = True
        threading.Thread(target=record_and_process).start()

def on_release(key):
    """Stop recording when key is released."""
    global rec_key_pressed
    if key == rec_key:
        rec_key_pressed = False

if __name__ == "__main__":
    if args.language:
        print(f"Using language: {args.language}")
    
    print(f"Press {rec_key} to start recording")
    with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        try:
            while listener.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")

