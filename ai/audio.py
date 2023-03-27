import openai


def get_audio_speech_to_text(filename, prompt, language='ru'):
    with open(filename, 'rb') as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file, prompt=prompt, language=language)
    return transcript.text