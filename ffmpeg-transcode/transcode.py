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
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove any existing handlers to avoid duplicates
    logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Stdout handler for info/debug messages
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    stdout_handler.setFormatter(formatter)

    # Stderr handler for warning/error messages
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)


def check_dependencies() -> bool:
    """Check if required command-line tools are available."""
    for tool in ['ffmpeg', 'ffprobe']:
        try:
            subprocess.run([tool, '-version'], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            logging.error(f"Required tool '{tool}' not found. Please install it.")
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

        logging.info("No English audio track found, defaulting to track 0")
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


def get_safe_output_path(source_file: str) -> str:
    """
    Generates an output file path, ensuring the filename does not exceed 
    the OS maximum filename length (usually 255 bytes on Linux).
    """
    directory = os.path.dirname(source_file)
    filename = os.path.basename(source_file)
    name_without_ext, _ = os.path.splitext(filename)
    
    suffix = "_RECODE.mp4"
    
    # Linux has a 255-byte limit for single filenames.
    # We set a safe limit of 240 bytes to avoid hitting edge-case filesystem limits.
    max_bytes = 240
    suffix_bytes = suffix.encode('utf-8')
    max_base_bytes = max_bytes - len(suffix_bytes)
    
    base_bytes = name_without_ext.encode('utf-8')
    
    if len(base_bytes) > max_base_bytes:
        # Truncate the byte string to fit within limits
        truncated_bytes = base_bytes[:max_base_bytes]
        # Decode back to string, ignoring any partial multi-byte UTF-8 character at the end
        truncated_name = truncated_bytes.decode('utf-8', errors='ignore')
        
        logging.warning(
            f"Filename '{filename}' is too long ({len(base_bytes)} bytes). "
            f"Truncating base name to stay within filesystem limits."
        )
        filename_to_use = f"{truncated_name}{suffix}"
    else:
        filename_to_use = f"{name_without_ext}{suffix}"
        
    return os.path.join(directory, filename_to_use)


def encode_file(source_file: str, audio_track: int) -> bool:
    """Encode the video file with settings optimized for direct streaming."""
    output_file = get_safe_output_path(source_file)

    if os.path.exists(output_file):
        logging.warning(f"Output file already exists, removing incomplete encode: {output_file}")
        try:
            os.remove(output_file)
            logging.info(f"Removed incomplete output file: {output_file}")
        except Exception as e:
            logging.error(f"Failed to remove existing output file {output_file}: {str(e)}")
            return False

    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', source_file,
        '-threads', '4',

        # --- Video settings ---
        '-vcodec', 'libx264',
        '-pix_fmt', 'yuv420p',

        # Constrain to High profile, level 4.1 — widely supported by
        # smart TVs, Roku, Chromecast, Fire Stick, browsers, etc.
        '-profile:v', 'high',
        '-level:v', '4.1',

        # Use CRF for consistent quality instead of a fixed bitrate.
        '-crf', '20',

        # Deinterlace only if needed (yadif always runs otherwise)
        '-vf', 'yadif=deint=interlaced',

        # --- Audio settings ---
        '-acodec', 'aac',
        '-ab', '128k',
        '-ac', '2',               # Stereo — maximum device compatibility
        '-aac_coder', 'twoloop',  # Better quality AAC encoding

        # --- Stream mapping ---
        '-map', '0:v:0',
        '-map', f'0:a:{audio_track}',

        # --- Container settings ---
        '-movflags', '+faststart',
        '-write_tmcd', '0',

        output_file
    ]

    try:
        logging.info(f"Starting encoding: {source_file}")
        logging.info(f"Output path generated: {output_file}")
        logging.info(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")

        subprocess.run(ffmpeg_cmd, check=True)

        # Verify the output file exists and has content
        if not os.path.exists(output_file) or os.path.getsize(output_file) < 1024:
            logging.error("Encoding failed: Output file is missing or empty")
            return False

        # Verify the output is actually playable
        verify_cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,profile,level,pix_fmt',
            '-of', 'json',
            output_file
        ]
        verify_output = subprocess.check_output(verify_cmd, stderr=subprocess.PIPE)
        verify_info = json.loads(verify_output)

        if not verify_info.get('streams'):
            logging.error("Verification failed: No video stream in output")
            return False

        stream = verify_info['streams'][0]
        logging.info(
            f"Output verified — codec: {stream.get('codec_name')}, "
            f"profile: {stream.get('profile')}, "
            f"level: {stream.get('level')}, "
            f"pix_fmt: {stream.get('pix_fmt')}"
        )

        logging.info(f"Successfully encoded: {output_file}")

        os.remove(source_file)
        logging.info(f"Removed source file: {source_file}")
        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg encoding failed with exit code {e.returncode}")
        # Clean up partial output
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
                logging.info("Cleaned up partial output file")
            except Exception as cleanup_err:
                logging.error(f"Failed to clean up output file {output_file}: {str(cleanup_err)}")
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

    # Sort for deterministic ordering in logs
    files_to_process.sort()

    logging.info(f"Found {len(files_to_process)} files to process in {base_path}")

    if files_to_process:
        logging.info("Files queued for encoding:")
        for i, file_path in enumerate(files_to_process, 1):
            try:
                size_gb = os.path.getsize(file_path) / (1024 * 1024 * 1024)
                logging.info(f"  [{i}/{len(files_to_process)}] {file_path} ({size_gb:.2f} GB)")
            except Exception as e:
                logging.warning(f"  [{i}/{len(files_to_process)}] {file_path} (size unavailable: {str(e)})")

    # Remove broken RECODE files
    try:
        for broken_file in glob.glob(f"{base_path}/**/*RECODE*", recursive=True):
            if os.path.getsize(broken_file) == 44:
                os.remove(broken_file)
                logging.info(f"Removed broken RECODE file: {broken_file}")
    except Exception as e:
        logging.error(f"Error cleaning broken RECODE files: {str(e)}")

    # Process the collected files
    for file_path in files_to_process:
        logging.info(f"Processing: {file_path}")
        try:
            audio_track = get_audio_track(file_path)
            if audio_track is not None and encode_file(file_path, audio_track):
                processed_count += 1
            else:
                error_count += 1
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
            error_count += 1

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

        logging.info(
            f"Processing complete. Successfully processed: {total_processed}, Errors: {total_errors}"
        )

        # Exit with error if any files failed
        if total_errors > 0:
            sys.exit(1)

    except Exception as e:
        logging.error(f"Fatal error in main process: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
