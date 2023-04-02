import json
import subprocess

from vosk import Model, KaldiRecognizer, SetLogLevel, SpkModel

SAMPLE_RATE = 16000

SetLogLevel(-1)

BIG_RUSSIAN_MODEL = 'vosk-model-ru-0.42'
SMALL_RUSSIAN_MODEL = 'vosk-model-small-ru-0.22'


def init_recognizer(model_name=SMALL_RUSSIAN_MODEL, lang="ru", words=None):
    model_params = {
        "lang": lang
    }
    if model_name:
        model_params['model_name'] = model_name

    model = Model(**model_params)
    if words:
        recognizer = KaldiRecognizer(model, SAMPLE_RATE, ' '.join(words))
    else:
        recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    return recognizer


def get_text(result):
    json_result = json.loads(result)
    if 'partial' in json_result:
        return json_result['partial'].strip()
    elif 'text' in json_result:
        return json_result['text'].strip()
    else:
        raise ValueError('Unknown key of result')


def process_audio(recognizer, audio_file_path):
    with subprocess.Popen(["ffmpeg", "-loglevel", "quiet", "-i",
                                audio_file_path,
                                "-ar", str(SAMPLE_RATE) , "-ac", "1", "-f", "s16le", "-"],
                                stdout=subprocess.PIPE) as process:

        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            recognizer.AcceptWaveform(data)

        final_result = get_text(recognizer.FinalResult())
        recognizer.Reset()
        return final_result
