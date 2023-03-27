import os

from audio.process import split_file_to_segments, SegmentInfo


def nickname_from_filename(input_recording_filename):
    _, name = input_recording_filename.split('-')
    name, _ = name.split('.')
    return name


def split_discord_files(input_files, output_folder):
    segment_infos = []

    for input_file in input_files:
        filename = os.path.basename(input_file)
        nickname = nickname_from_filename(filename)

        print(f'Splitting file', input_file)
        segments = split_file_to_segments(input_file, output_folder, nickname)
        segment_infos += [SegmentInfo(filename, nickname, start_time, end_time) for filename, start_time, end_time in segments]

    return segment_infos
