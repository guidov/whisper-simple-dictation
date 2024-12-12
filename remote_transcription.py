import os
import soundfile
from openai import OpenAI

def get_text_remote(audio, language=None, context=None, use_groq=False):
    """Transcribe audio using remote API (OpenAI or Groq)."""
    tmp_audio_filename = "tmp.wav"
    soundfile.write(tmp_audio_filename, audio, 16000, format="wav")
    
    if use_groq:
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )
        model = "whisper-large-v3"
    else:
        client = OpenAI(
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        model = "whisper-1"

    try:
        api_response = client.audio.transcriptions.create(
            model=model,
            file=open(tmp_audio_filename, "rb"),
            language=language
        )
        return api_response.text
    finally:
        if os.path.exists(tmp_audio_filename):
            os.remove(tmp_audio_filename)
