# Whisper Simple Dictation

A simple speech-to-text dictation tool using Whisper that supports both local and remote transcription.

## Features
- Press right Ctrl to record, release to transcribe
- Local transcription using Whisper (near instant)
- Remote transcription using OpenAI or Groq API
- Automatic text insertion at cursor position
## Limitations
- Does not work in regualar terminals/applications using X11/Wayland
- I suggest using Electron/TS based terminals (e.g. Waveterm https://github.com/wavetermdev/waveterm)

## Installation

```bash
# Clone the repository
git clone https://github.com/guidov/whisper-simple-dictation.git
cd whisper-simple-dictation

# Create conda environment
conda create -n whisperdict python=3.10
conda activate whisperdict
sudo apt install portaudio19-dev
conda install -c conda-forge libstdcxx-ng

# add your username to the group input and relogin or reboot
sudo usermod -aG input $USER


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
- Works fine with CPU also
- Internet connection for remote transcription
- Linux with X11 or Wayland

## Running as a Service

The dictation tool can be run as a systemd user service that starts automatically with your session:

1. Create the service file:
```bash
mkdir -p ~/.config/systemd/user/
cat > ~/.config/systemd/user/whisper-dictation.service << 'EOF'
[Unit]
Description=Whisper Dictation Service

[Service]
ExecStart=/bin/bash -c "source /home/guido/anaconda3/etc/profile.d/conda.sh && conda activate whisperdict && cd /home/guido/whisper-simple-dictation && ./run_dictation_local.sh en"
StandardOutput=file:/home/guido/logs/whisper-dictation.log
StandardError=file:/home/guido/logs/whisper-dictation.log
Restart=always

[Install]
WantedBy=default.target
EOF
```

2. Create logs directory:
```bash
mkdir -p ~/logs
```

3. Enable and start the service:
```bash
systemctl --user daemon-reload
systemctl --user enable whisper-dictation.service
systemctl --user start whisper-dictation.service
```

4. Check service status:
```bash
systemctl --user status whisper-dictation.service
```

The service will automatically restart if it fails and start on login. You can:
- Stop the service: `systemctl --user stop whisper-dictation.service`
- Start the service: `systemctl --user start whisper-dictation.service`
- View logs: `tail -f ~/logs/whisper-dictation.log`

Note: Update the paths in the service file to match your conda and project locations.
