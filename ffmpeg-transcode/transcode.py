#!/usr/bin/env python3

import os
import subprocess
import json
import glob
from pathlib import Path


def get_audio_track(input_file):
    ffprobe_cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        '-select_streams', 'a',
        input_file
    ]
    output = subprocess.check_output(ffprobe_cmd)
    info = json.loads(output)
    audio_streams = info['streams']

    # Find English track or default to 0
    for i, stream in enumerate(audio_streams):
        if 'tags' in stream and 'language' in stream['tags'] and stream['tags']['language'].lower() == 'eng':
            return i
    return 0


def encode_file(source_file, audio_track):
    output_file = f"{os.path.splitext(source_file)[0]}_RECODE.mp4"

    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', source_file,
        '-threads', '2',
        '-vcodec', 'libx264',
        '-b:v', '1200k',
        '-filter:v', 'yadif',
        '-acodec', 'aac',
        '-ab', '128k',
        '-map', '0:v:0',
        '-map', f'0:a:{audio_track}',
        output_file
    ]

    print(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
    subprocess.run(ffmpeg_cmd, check=True)
    os.remove(source_file)


def process_directory(base_path, min_size_mb):
    # Convert MB to bytes
    min_size = min_size_mb * 1024 * 1024

    # Remove broken RECODE files
    for broken_file in glob.glob(f"{base_path}/**/*RECODE*", recursive=True):
        if os.path.getsize(broken_file) == 44:
            os.remove(broken_file)

    # Find media files
    extensions = ['mp4', 'mpeg4', 'mkv', 'avi']
    for ext in extensions:
        pattern = f"{base_path}/**/*.{ext}"
        for file_path in glob.glob(pattern, recursive=True):
            # Skip files with _RECODE or _SKIP in name
            if '_RECODE' in file_path or '_SKIP' in file_path:
                continue

            # Check file size
            if os.path.getsize(file_path) >= min_size:
                print(f"Processing: {file_path}")
                try:
                    audio_track = get_audio_track(file_path)
                    encode_file(file_path, audio_track)
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")


def main():
    # Process TV Shows
    process_directory('/library/TV Shows', 390)

    # Process Movies
    process_directory('/library/Movies', 2000)


if __name__ == '__main__':
    main()
