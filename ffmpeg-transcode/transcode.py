#!/usr/bin/env python3

import os
import subprocess
import json
import glob
from pathlib import Path
import logging
import sys
from typing import Optional, Tuple


def setup_logging() -> None:
    """Configure logging to stdout/stderr for container environment"""
    # Configure root logger to stderr for errors
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )

    # Create stdout handler for info/debug messages
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)

    # Create stderr handler for warning/error messages
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)

    # Get root logger and add handlers
    logger = logging.getLogger()
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)


def check_dependencies() -> bool:
    """Check if required command-line tools are available."""
    for tool in ['ffmpeg', 'ffprobe']:
        try:
            subprocess.run([tool, '-version'], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            logging.error(f"Required tool '{
                          tool}' not found. Please install it.")
            return False
    return True


def get_audio_track(input_file: str) -> Optional[int]:
    """Get the appropriate audio track number."""
    try:
        ffprobe_cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            '-select_streams', 'a',
            input_file
        ]
        output = subprocess.check_output(ffprobe_cmd, stderr=subprocess.PIPE)
        info = json.loads(output)

        if not info.get('streams'):
            logging.warning(f"No audio streams found in {input_file}")
            return None

        audio_streams = info['streams']

        # Find English track or default to 0
        for i, stream in enumerate(audio_streams):
            if 'tags' in stream and 'language' in stream['tags'] and stream['tags']['language'].lower() == 'eng':
                logging.info(f"Found English audio track at index {i}")
                return i

        logging.info(f"No English audio track found, defaulting to track 0")
        return 0

    except subprocess.CalledProcessError as e:
        logging.error(f"FFprobe error for {input_file}: {e.stderr.decode()}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error for {input_file}: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in get_audio_track: {str(e)}")
        raise


def encode_file(source_file: str, audio_track: int) -> bool:
    """Encode the video file with error handling."""
    output_file = f"{os.path.splitext(source_file)[0]}_RECODE.mp4"

    if os.path.exists(output_file):
        logging.warning(f"Output file already exists: {output_file}")
        return False

    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', source_file,
        '-threads', '4',
        '-vcodec', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-b:v', '1200k',
        '-filter:v', 'yadif',
        '-acodec', 'aac',
        '-ab', '128k',
        '-map', '0:v:0',
        '-map', f'0:a:{audio_track}',
        output_file
    ]

    try:
        logging.info(f"Starting encoding: {source_file}")
        logging.info(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")

        subprocess.run(ffmpeg_cmd, check=True)

        # Verify the output file exists and has content
        if not os.path.exists(output_file) or os.path.getsize(output_file) < 1024:
            logging.error(f"Encoding failed: Output file is missing or empty")
            return False

        logging.info(f"Successfully encoded: {output_file}")

        # Remove source file
        os.remove(source_file)
        logging.info(f"Removed source file: {source_file}")
        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg encoding failed")
        return False
    except Exception as e:
        logging.error(f"Encoding error: {str(e)}")
        return False


def process_directory(base_path: str, min_size_mb: int) -> Tuple[int, int]:
    """Process directory with error tracking."""
    if not os.path.exists(base_path):
        logging.error(f"Directory not found: {base_path}")
        return 0, 0

    min_size = min_size_mb * 1024 * 1024
    processed_count = 0
    error_count = 0

    # Build a list of files that need processing
    files_to_process = []
    extensions = ['mp4', 'mpeg4', 'mkv', 'avi']
    for ext in extensions:
        pattern = f"{base_path}/**/*.{ext}"
        try:
            for file_path in glob.glob(pattern, recursive=True):
                if '_RECODE' in file_path or '_SKIP' in file_path:
                    continue
                if os.path.getsize(file_path) >= min_size:
                    files_to_process.append(file_path)
        except Exception as e:
            logging.error(f"Error scanning for {ext} files: {str(e)}")

    logging.info(
        f"Found {len(files_to_process)} files to process in {base_path}")

    # Remove broken RECODE files
    try:
        for broken_file in glob.glob(f"{base_path}/**/*RECODE*", recursive=True):
            if os.path.getsize(broken_file) == 44:
                os.remove(broken_file)
                logging.info(f"Removed broken RECODE file: {broken_file}")
    except Exception as e:
        logging.error(f"Error cleaning broken RECODE files: {str(e)}")

    # Find media files
    for ext in extensions:
        pattern = f"{base_path}/**/*.{ext}"
        try:
            for file_path in glob.glob(pattern, recursive=True):
                if '_RECODE' in file_path or '_SKIP' in file_path:
                    continue

                if os.path.getsize(file_path) >= min_size:
                    logging.info(f"Processing: {file_path}")
                    try:
                        audio_track = get_audio_track(file_path)
                        if audio_track is not None and encode_file(file_path, audio_track):
                            processed_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        logging.error(
                            f"Error processing {file_path}: {str(e)}")
                        error_count += 1
                else:
                    logging.debug(f"Skipping file (too small): {file_path}")

        except Exception as e:
            logging.error(f"Error processing extension {ext}: {str(e)}")

    return processed_count, error_count


def main():
    setup_logging()
    logging.info("Starting video processing script")

    if not check_dependencies():
        logging.error("Required dependencies not found. Exiting.")
        sys.exit(1)

    total_processed = 0
    total_errors = 0

    try:
        # Process TV Shows
        logging.info("Processing TV Shows directory")
        processed, errors = process_directory('/library/TV Shows', 390)
        total_processed += processed
        total_errors += errors

        # Process Movies
        logging.info("Processing Movies directory")
        processed, errors = process_directory('/library/Movies', 2000)
        total_processed += processed
        total_errors += errors

        logging.info(f"Processing complete. Successfully processed: {
                     total_processed}, Errors: {total_errors}")

        # Exit with error if any files failed
        if total_errors > 0:
            sys.exit(1)

    except Exception as e:
        logging.error(f"Fatal error in main process: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
