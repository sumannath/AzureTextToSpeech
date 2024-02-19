from moviepy.editor import VideoFileClip, AudioFileClip


def loop_video_with_audio(video_path, audio_path, output_path):
    # Load the video clip
    video_clip = VideoFileClip(video_path)

    # Load the audio clip
    audio_clip = AudioFileClip(audio_path)

    # Set the video clip duration to match the audio clip
    video_clip = video_clip.set_duration(audio_clip.duration)

    # Concatenate the video clips to create a loop
    looped_clip = video_clip.loop(duration=audio_clip.duration)

    # Set the audio of the final clip to the background audio
    final_clip = looped_clip.set_audio(audio_clip)

    # Write the final clip to an output file
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    print(f"Video with audio looped successfully. Output file: {output_path}")


if __name__ == "__main__":
    # Example usage:
    video_path = "data/loops/sunset_and_the_couple.mov"
    audio_path = "outputaudio.mp3"
    output_path = "output_loop_video.mp4"

    loop_video_with_audio(video_path, audio_path, output_path)
