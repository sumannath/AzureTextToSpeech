import os.path

# Set Application Paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_DIR, "data")
BIN_DIR = os.path.join(APP_DIR, "bin")
RUNS_DIR = os.path.join(APP_DIR, "runs")
LOOP_VIDEO_DIR = os.path.join(DATA_DIR, "loops")
OP_DIR = os.path.join(DATA_DIR, "op")

# Speech Settings
SPEECH_VOICE = 'bn-IN-TanishaaNeural'

# Files
INPUT_TEXT = os.path.join(DATA_DIR, "input.txt")
LOOP_VIDEO = os.path.join(LOOP_VIDEO_DIR, "sunset_and_the_couple.mov")
OUTPUT_MP3 = "mp3_output.mp3"
OUTPUT_VIDEO = "final_opt.mp4"
