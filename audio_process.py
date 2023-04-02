import os
from glob import glob

from ai import init_openai
from ai.completion import get_summary
from audio.discord import split_discord_files
from audio_transcription.transcribe import transcribe_with_vosk, transcribe_with_openai

AUDIO_INPUT_FORMAT = 'ogg'
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


# split string to parts of size
def split_string(string, size):
    return [string[i:i + size] for i in range(0, len(string), size)]


def get_text_buckets(texts, max_bucket_length=2048):
    buckets = []
    str_bucket = ''
    processed_texts = []
    for line in texts:
        if len(line) >= max_bucket_length:
            nickname, *_ = line.split(': ')
            text = line[len(nickname) + 2:]
            texts = [f'{nickname}: {text_part}' for text_part in split_string(text, max_bucket_length - len(nickname) - 2)]
            processed_texts += texts
        else:
            processed_texts.append(line)

    for line in processed_texts:
        if len(str_bucket + line) + 1 >= max_bucket_length and len(str_bucket) != 0:
            buckets.append(str_bucket)
            str_bucket = ''
        str_bucket = line if len(str_bucket) == 0 else str_bucket + '\n' + line
    else:
        if len(str_bucket) != 0:
            buckets.append(str_bucket)
    return buckets


def summarize_down(to_summarize, max_bucket_length=2048, max_summary_length=2000, out_summaries_count=2):
    """ Split text to bucket_max_length buckets and summarize buckets down to out_summaries_count summaries """
    while True:
        summaries = []
        buckets = get_text_buckets(to_summarize, max_bucket_length)
        print("\n\nWe have {} buckets".format(len(buckets)))
        for bucket in buckets:
            print("-------------------------------")
            print("Generating summary for bucket: ")
            print(bucket)
            summary = get_summary(bucket, max_summary_length)
            summaries.append(summary)
        if len(summaries) <= out_summaries_count:
            break
        else:
            to_summarize = summaries
    return summaries


def calculate_segments_length(segment_infos):
    # calculate length of full recording
    full_recording_length = 0
    for segment_info in segment_infos:
        full_recording_length += segment_info.end_time - segment_info.start_time

    return full_recording_length / 1000  # seconds


def filter_hallucinations(texts):
    result = []
    for text in texts:
        processed_text = text.lower().strip()

        if 'игорь негода' in processed_text:
            continue
        if any([processed_text.count(letter * 6) > 0 for letter in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя']):
            continue

        result.append(text)
    return result


if __name__ == '__main__':
    init_openai(OPENAI_API_KEY)

    files_removed = delete_all_files(AUDIO_OUTPUT_FOLDER)
    if files_removed:
        print(f'Removed {files_removed} files from {AUDIO_OUTPUT_FOLDER} folder')

    input_files = glob(os.path.join(AUDIO_INPUT_FOLDER, f'*.{AUDIO_INPUT_FORMAT}'))
    if len(input_files) == 0:
        print('No files found')
        exit(1)
    print('Found files:', len(input_files))

    # split files to segments
    segment_infos = split_discord_files(input_files, AUDIO_OUTPUT_FOLDER)

    # sort by start time
    segment_infos = sorted(segment_infos, key=lambda x: x.start_time)

    full_recording_length = calculate_segments_length(segment_infos)
    print("Est. transcription cost: $", full_recording_length / 60 * 0.006)

    result_texts = transcribe_with_openai(segment_infos, RECORDING_CONTEXT, RECORDING_LANGUAGE)
    # result_texts = transcribe_with_vosk(segment_infos, RECORDING_LANGUAGE)

    result_texts = filter_hallucinations(result_texts)

    result_text = '\n'.join(result_texts)
    print()
    print(result_text)
    with open(f'result_text.txt', 'w') as file:
        file.write(result_text)

    summaries = summarize_down(result_texts, max_bucket_length=3000, max_summary_length=1024, out_summaries_count=4)

    print('Summary:')
    print('\n'.join(summaries))
