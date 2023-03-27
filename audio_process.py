import os
from glob import glob

from ai import init_openai
from ai.audio import get_audio_speech_to_text
from ai.completion import get_summary, get_json_summary
from audio.discord import split_discord_files

AUDIO_INPUT_FOLDER = 'input_audio/lafleuere-test/'
AUDIO_OUTPUT_FOLDER = 'temp_output'

OPENAI_API_KEY = ''

RECORDING_LANGUAGE = 'ru'
RECORDING_CONTEXT = ''


def delete_all_files(directory):
    if not os.path.exists(directory):
        raise ValueError(f"Directory '{directory}' does not exist.")

    count = 0
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            count += 1
        else:
            print(f"Skipping non-file item: {file_path}")

    return count


if __name__ == '__main__':
    init_openai(OPENAI_API_KEY)

    files_removed = delete_all_files(AUDIO_OUTPUT_FOLDER)
    if files_removed:
        print(f'Removed {files_removed} files from {AUDIO_OUTPUT_FOLDER} folder')

    input_files = glob(os.path.join(AUDIO_INPUT_FOLDER, '*.ogg'))
    print('Found files:', len(input_files))

    # split files to segments
    segment_infos = split_discord_files(input_files, AUDIO_OUTPUT_FOLDER)

    # sort by start time
    segment_infos = sorted(segment_infos, key=lambda x: x.start_time)

    result_text = ''
    # prompt_text used as prompt to increase accuracy
    prompt_text = f'{RECORDING_CONTEXT}\n' if len(RECORDING_CONTEXT) > 0 else ''
    for segment_info in segment_infos:
        print(f'Processing {segment_info.filename}')
        text = get_audio_speech_to_text(segment_info.filename, prompt_text, RECORDING_LANGUAGE)
        result_text += f'{segment_info.nickname}: {text}\n'
        prompt_text += f'{text}\n'

    print()
    print(result_text)

    summary = get_summary(result_text)
    print('Summary:')
    print(summary)

    json_summary = get_json_summary(result_text)
    print('JSON Summary:')
    print(json_summary)
