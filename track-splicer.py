import os
import shutil
from pydub import AudioSegment

# Supported audio formats
SUPPORTED_FORMATS = ('.mp3', '.wav', '.ogg', '.flac')

# Define input and output paths
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

# Make sure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def split_audio_file(filepath, segment_length, fade_length, overlap_length=500):
    audio = AudioSegment.from_file(filepath)
    file_duration = len(audio)

    # Extract file name without extension
    filename = os.path.splitext(os.path.basename(filepath))[0]

    # Create specific output directory structure
    base_output_dir = os.path.join(OUTPUT_FOLDER, filename)
    full_output_dir = os.path.join(base_output_dir, "full")
    fadein_output_dir = os.path.join(base_output_dir, "fadein")
    fadeout_output_dir = os.path.join(base_output_dir, "fadeout")

    # Clear previous output if exists
    for directory in [full_output_dir, fadein_output_dir, fadeout_output_dir]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory, exist_ok=True)

    segment_length_ms = segment_length * 1000

    # Split audio
    for i, start_time in enumerate(range(0, file_duration, segment_length_ms)):
        end_time = min(start_time + segment_length_ms + overlap_length, file_duration)
        segment = audio[start_time:end_time]

        # Apply fades for overlapping (normal segments)
        overlap_segment = segment.fade_out(overlap_length).fade_in(overlap_length)

        # Original segment with overlap
        full_file = os.path.join(full_output_dir, f"{filename}{i+1}.ogg")
        overlap_segment.export(full_file, format="ogg")
        print(f"Exported {full_file}")

        # Fade-in segment with overlap at the end
        fadein_segment = segment[:segment_length_ms + overlap_length].fade_in(fade_length * 1000).fade_out(overlap_length)
        fadein_file = os.path.join(fadein_output_dir, f"{filename}{i+1}in.ogg")
        fadein_segment.export(fadein_file, format="ogg")
        print(f"Exported {fadein_file}")

        # Fade-out segment with overlap at the beginning
        fadeout_segment = segment[:segment_length_ms + overlap_length].fade_out(fade_length * 1000).fade_in(overlap_length)
        fadeout_file = os.path.join(fadeout_output_dir, f"{filename}{i+1}out.ogg")
        fadeout_segment.export(fadeout_file, format="ogg")
        print(f"Exported {fadeout_file}")

def main():
    # Ask user for segment length
    try:
        segment_length = int(input("Segment length in seconds (default 12): ") or "12")
    except ValueError:
        print("Invalid input, defaulting to 12 seconds.")
        segment_length = 12

    # Ask user for fade length
    try:
        fade_length = int(input("Fade length in seconds (default 2): ") or "2")
    except ValueError:
        print("Invalid input, defaulting to 2 seconds.")
        fade_length = 2

    # Overlap length is fixed at 0.5 seconds (500ms)
    overlap_length = 500

    # Process each file in the input folder
    for file in os.listdir(INPUT_FOLDER):
        if file.lower().endswith(SUPPORTED_FORMATS):
            filepath = os.path.join(INPUT_FOLDER, file)
            print(f"Processing {filepath}...")
            split_audio_file(filepath, segment_length, fade_length, overlap_length)

if __name__ == "__main__":
    main()
