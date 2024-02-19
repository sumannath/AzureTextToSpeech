import subprocess


def loop_video_to_audio_length(input_video, input_audio, output_video):
    # Set the target video bitrate to 5000 kbps
    target_bitrate = 5000

    # Create a list representing the ffmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-stream_loop', '-1',
        '-i', input_video,
        '-i', input_audio,
        '-shortest',
        '-c:v', 'h264_nvenc',
        '-b:v', f'{target_bitrate}k',
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-y',
        output_video
    ]

    # Run the ffmpeg command
    subprocess.run(ffmpeg_command)

    print(f"Video looped to audio length successfully. Output file: {output_video}")


if __name__ == "__main__":
    # Example usage:
    input_video = "sunset_and_the_couple.mov"
    input_audio = "outputaudio.mp3"
    output_video = "output_loop_to_audio_length.mov"

    loop_video_to_audio_length(input_video, input_audio, output_video)
