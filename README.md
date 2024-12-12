# Whisper Simple Dictation

A simple speech-to-text dictation tool using Whisper that supports both local and remote transcription.

## Features
- Press right Ctrl to record, release to transcribe
- Local transcription using Whisper (near instant)
- Remote transcription using OpenAI or Groq API
- Automatic text insertion at cursor position

## Installation

```bash
# Clone the repository
git clone https://github.com/guidov/whisper-simple-dictation.git
cd whisper-simple-dictation

# Create conda environment
conda create -n whisperdict python=3.10
conda activate whisperdict

# Install dependencies
# For local transcription:
pip install -r requirements_local.txt

# For remote transcription:
pip install -r requirements_remote.txt
```

For remote transcription, set up your API keys:
```bash
# For OpenAI:
export OPENAI_API_KEY=your_key_here

# For Groq:
export GROQ_API_KEY=your_key_here
```

## Usage

For local transcription (using local Whisper model):
```bash
./run_dictation_local.sh
```

For remote transcription (using OpenAI or Groq):
```bash
./run_dictation_remote.sh
```

Hold the right Ctrl key while speaking, then release it to transcribe. Press Ctrl-C to exit.

## Options

- Language: Add language code as argument (e.g., `./run_dictation_local.sh en`)
- Model: Default is small.en for local. Can be changed in dictation.py
- API: Use --use-groq flag for Groq API instead of OpenAI

## Requirements

- Python 3.10+
- CUDA-capable GPU for local transcription
- Internet connection for remote transcription
- Linux with X11 or Wayland
