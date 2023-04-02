import os
from concurrent.futures import ProcessPoolExecutor
from typing import List

from audio.process import split_file_to_segments, SegmentInfo


AUDIO_PROCESSING_CONCURRENCY = 5


def nickname_from_filename(input_recording_filename):
    _, name = input_recording_filename.split('-')
    name, _ = name.split('.')
    return name


def split_discord_files(input_files, output_folder) -> List[SegmentInfo]:
    segment_infos = []

    with ProcessPoolExecutor(max_workers=AUDIO_PROCESSING_CONCURRENCY) as executor:
        futures = []
        for input_file in input_files:
            filename = os.path.basename(input_file)
            nickname = nickname_from_filename(filename)

            future = executor.submit(split_file_to_segments, input_file, output_folder, nickname)
            futures.append((future, nickname))

        for future, nickname in futures:
            segments = future.result()
            segment_infos += [SegmentInfo(filename, nickname, start_time, end_time) for filename, start_time, end_time in segments]

    return segment_infos
