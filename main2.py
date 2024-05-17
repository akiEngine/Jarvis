import warnings
import tempfile
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play
import threading
import openai
import io
import soundfile as sf
import sounddevice as sd

client = OpenAI()

warnings.filterwarnings("ignore", category=DeprecationWarning)

spoken_response = client.audio.speech.create(
  model="tts-1-hd",
  voice="fable",
  response_format="opus",
  input="just tell me something really nice, Whispers of the wind weave tales of forgotten dreams beneath the moonlit sky., Whispers of the wind weave tales of forgotten dreams beneath the moonlit sky., Whispers of the wind weave tales of forgotten dreams beneath the moonlit sky."
)

buffer = io.BytesIO()
for chunk in spoken_response.iter_bytes(chunk_size=4096):
  buffer.write(chunk)
buffer.seek(0)

with sf.SoundFile(buffer, 'r') as sound_file:
  data = sound_file.read(dtype='int16')
  sd.play(data, sound_file.samplerate)
  sd.wait()