import os
import soundfile
from openai import OpenAI

def get_text_remote(audio, language=None, context=None, use_groq=False):
    tmp_audio_filename = "tmp.wav"
    soundfile.write(tmp_audio_filename, audio, 16000, format="wav")
    if use_groq:
        groq_api_key=os.getenv("GROQ_API_KEY")
        client = OpenAI(base_url="https://api.groq.com/openai/v1",
                        api_key=groq_api_key
                        )
        model = "whisper-large-v3"
    else:
        openai_api_key=os.getenv("OPENAI_API_KEY")
        client = OpenAI(base_url="https://api.openai.com/v1",
                        api_key=openai_api_key)
        model = "whisper-1"

    api_response = client.audio.transcriptions.create(
        model=model,
        file=open(tmp_audio_filename, "rb"),
        language=language,
        prompt=context,
    )

    return api_response.text
