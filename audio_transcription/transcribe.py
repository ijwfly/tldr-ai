from ai.audio import get_audio_speech_to_text
from audio_transcription.vosk.transcribe import init_recognizer, process_audio


def transcribe_with_vosk(segment_infos, language):
    result_texts = []
    recognizer = init_recognizer(lang=language)
    for segment_info in segment_infos:
        print(f'Processing {segment_info.filename}')
        text = process_audio(recognizer, segment_info.filename)
        if len(text) == 0:
            continue
        result_texts.append(f'{segment_info.nickname}: {text}')
    return result_texts


def transcribe_with_openai(segment_infos, recording_context, language):
    result_texts = []
    prompt_text = f'{recording_context}\n' if len(recording_context) > 0 else ''
    for segment_info in segment_infos:
        print(f'Processing {segment_info.filename}')
        text = get_audio_speech_to_text(segment_info.filename, prompt_text, language)
        if len(text) == 0:
            continue
        result_texts.append(f'{segment_info.nickname}: {text}')
        # openai ignores prompt length more than 300 tokens
        prompt_text = (prompt_text + f'{text}')[:300]
    return result_texts


