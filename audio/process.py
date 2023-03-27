import dataclasses
import itertools
import os

from pydub import AudioSegment
from pydub.silence import detect_nonsilent

MIN_SILENCE_LEN = 2000  # ms
SILENCE_THRESHOLD = -30  # dBFS


@dataclasses.dataclass
class SegmentInfo:
    filename: str
    nickname: str
    start_time: int
    end_time: int


def split_on_silence(audio_segment, min_silence_len=1000, silence_thresh=-16, keep_silence=300, seek_step=1):
    # from the itertools documentation
    def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = itertools.tee(iterable)
        next(b, None)
        return zip(a, b)

    if isinstance(keep_silence, bool):
        keep_silence = len(audio_segment) if keep_silence else 0

    output_ranges = [
        [start - keep_silence, end + keep_silence]
        for (start, end)
        in detect_nonsilent(audio_segment, min_silence_len, silence_thresh, seek_step)
    ]

    for range_i, range_ii in pairwise(output_ranges):
        last_end = range_i[1]
        next_start = range_ii[0]
        if next_start < last_end:
            range_i[1] = (last_end + next_start) // 2
            range_ii[0] = range_i[1]

    result_segments = []
    for start, end in output_ranges:
        segment_start = max(start, 0)
        segment_end = min(end, len(audio_segment))
        segment = audio_segment[segment_start:segment_end]

        result_tuple = (segment_start, segment_end, segment)
        result_segments.append(result_tuple)

    return result_segments


def split_file_to_segments(input_file, output_folder, output_file_prefix, min_silence_len=MIN_SILENCE_LEN, silence_thresh=SILENCE_THRESHOLD):
    audio = AudioSegment.from_file(input_file)
    voice_segments = split_on_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

    output_segments = []
    for i, segment in enumerate(voice_segments):
        output_segments.append(segment)

    filenames_with_timings = []
    for i, segment in enumerate(output_segments):
        start_time_ms, end_time_ms, audio_segment = segment
        output_filename = f"{output_file_prefix}_{i + 1}_{start_time_ms:08d}-{end_time_ms:08d}.wav"
        output_filename = os.path.join(output_folder, output_filename)
        audio_segment.export(output_filename, format="wav")
        filenames_with_timings.append((output_filename, start_time_ms, end_time_ms))
        print(f"Saved {output_filename}")

    return filenames_with_timings

