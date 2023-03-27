import openai


def get_audio_speech_to_text(filename, prompt, language='ru', temperature=0):
    with open(filename, 'rb') as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file, prompt=prompt, language=language, temperature=temperature)
    return transcript.text
