import logging
import os
import shutil
import subprocess
import time
from datetime import datetime

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import asyncio

import config


def setup_logging(run_id):
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    log_file_path = os.path.join(config.RUNS_DIR, run_id, 'run.log')

    # Create a file handler and set the formatter
    file_handler = logging.FileHandler(str(log_file_path))
    file_formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)

    # Create a console handler and set the formatter
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)

    # Get the root logger and add both handlers
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


async def synthesize_file_to_mp3_file(input_file, audio_file):
    load_dotenv()

    # Your subscription key and service region. Set in .env file
    subscription_key = os.environ.get('SPEECH_KEY')
    service_region = os.environ.get('SPEECH_REGION')

    # Creates an instance of a speech config with specified subscription key and service region.
    # The default language is "en-us".
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)

    speech_config.speech_synthesis_voice_name = config.SPEECH_VOICE

    # Sets the synthesis output format.
    # The full list of supported format can be found here:
    # https://docs.microsoft.com/azure/cognitive-services/speech-service/rest-text-to-speech#audio-outputs
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

    # Read the plain text file. A simple logic is to split by lines which is a paragraph.
    # Assume a paragraph won't exceed 10 min limit here.
    with open(input_file, "r", encoding="utf-8") as file:
        paragraphs = file.readlines()

    retry_count = 10
    stopwatch = time.time()

    # Creates a speech synthesizer using file as audio output.
    # Replace with your own audio file name.
    file_name = audio_file
    file_output = speechsdk.audio.AudioOutputConfig(filename=file_name)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_output)

    para_cnt = 1
    for paragraph in paragraphs:
        if len(paragraph.strip()) == 0:
            continue
        retry = retry_count
        while retry > 0:
            result = synthesizer.speak_text_async(paragraph).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"Success on paragragh {para_cnt}! ID: {result.result_id} in {time.time() - stopwatch} seconds")
                break
            elif result.reason == speechsdk.ResultReason.Canceled:
                print(f"Failed on {paragraph} {result.result_id}")
                cancellation = speechsdk.SpeechSynthesisCancellationDetails(result=result)
                print(f"CANCELED: Reason={cancellation.reason}")

                if cancellation.reason == speechsdk.CancellationReason.Error:
                    print(f"CANCELED: ErrorCode={cancellation.error_code}")
                    print(f"CANCELED: ErrorDetails=[{cancellation.error_details}]")
                    print("CANCELED: Did you update the subscription info?")

            retry -= 1
            print("Retrying again...")


def loop_video_to_audio_length(input_video, input_audio, output_video):
    # Set the target video bitrate to 5000 kbps
    target_bitrate = 5000

    # Create a list representing the ffmpeg command
    ffmpeg_command = [
        f'{os.path.join(config.BIN_DIR, "ffmpeg")}',
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
    current_datetime = datetime.now()
    run_id = f"run_{current_datetime.strftime("%Y%m%d_%H%M%S")}"

    if os.path.exists(config.RUNS_DIR):
        if not os.path.isdir(config.RUNS_DIR):
            raise FileExistsError("The 'runs' path exists but is not a directory. Please check")
    else:
        os.mkdir(config.RUNS_DIR)

    run_dir_path = os.path.join(config.RUNS_DIR, run_id)
    os.mkdir(run_dir_path)

    setup_logging(run_id=run_id)
    logging.info(f"Starting run, Run ID: {run_id}")
    logging.info(f"Run dir: {run_dir_path}")

    if os.path.exists(config.INPUT_TEXT):
        if not os.path.isfile(config.INPUT_TEXT):
            raise FileNotFoundError("The input file path exists but is not a file")
    else:
        raise FileNotFoundError("The input file does not exist")

    shutil.copy(config.INPUT_TEXT, run_dir_path)

    logging.info("Starting creation of MP3 audio file...")

    mp3_filepath = os.path.join(run_dir_path, config.OUTPUT_MP3)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        synthesize_file_to_mp3_file(
            input_file=config.INPUT_TEXT,
            audio_file=mp3_filepath
        )
    )

    logging.info(f"MP3 audio file completed. File saved at: {mp3_filepath}")

    logging.info("Starting creation of loop video...")

    video_filepath = os.path.join(run_dir_path, config.OUTPUT_VIDEO)
    loop_video_to_audio_length(
        input_video=config.LOOP_VIDEO,
        input_audio=mp3_filepath,
        output_video=video_filepath
    )

    logging.info(f"Video file completed. File saved at: {video_filepath}")
