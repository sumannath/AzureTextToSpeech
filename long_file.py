import os
import time
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv


async def synthesis_file_to_mp3_file():
    load_dotenv()

    # Replace with your own subscription key and service region (e.g., "westus").
    subscription_key = os.environ.get('SPEECH_KEY')
    service_region = os.environ.get('SPEECH_REGION')

    # Creates an instance of a speech config with specified subscription key and service region.
    # The default language is "en-us".
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)

    speech_config.speech_synthesis_voice_name = 'bn-IN-TanishaaNeural'

    # Sets the synthesis output format.
    # The full list of supported format can be found here:
    # https://docs.microsoft.com/azure/cognitive-services/speech-service/rest-text-to-speech#audio-outputs
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

    # Read the plain text file. A simple logic is to split by lines which is a paragraph.
    # Assume a paragraph won't exceed 10 min limit here.
    with open("data/input.txt", "r", encoding="utf-8") as file:
        paragraphs = file.readlines()

    retry_count = 10
    stopwatch = time.time()

    # Creates a speech synthesizer using file as audio output.
    # Replace with your own audio file name.
    file_name = "outputaudio.mp3"
    file_output = speechsdk.audio.AudioOutputConfig(filename=file_name)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_output)

    for paragraph in paragraphs:
        if len(paragraph.strip()) == 0:
            continue
        retry = retry_count
        while retry > 0:
            result = synthesizer.speak_text_async(paragraph).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"Success on {paragraph} {result.result_id} in {time.time() - stopwatch} seconds")
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


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(synthesis_file_to_mp3_file())
