import pyaudio
import wave
import openai
from openai import OpenAI
import audioop
import time
import os
from pocketsphinx import LiveSpeech, get_model_path
from eff_word_net.streams import SimpleMicStream
from eff_word_net.engine import HotwordDetector
from eff_word_net.audio_processing import Resnet50_Arc_loss
from dimits import Dimits
dt = Dimits("fr_FR-siwis-medium")

client = OpenAI()

def speech_to_text():
    API_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = API_KEY
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = "output.wav"
    THRESHOLD = 300  # Niveau pour démarrer l'enregistrement
    SILENCE_LIMIT = 1.5  # Temps de silence avant d'arrêter l'enregistrement (en secondes)
    silence_count = 0

    audio = pyaudio.PyAudio()

    print("Initialisation de l'enregistrement...")

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []
    
    # Détecter le niveau sonore avant de commencer à enregistrer
    data = stream.read(CHUNK)
    audio_level = audioop.rms(data, 2)
    started_recording = 0

    # Enregistrement de l'audio après la détection de la parole
    while True:
        data = stream.read(CHUNK)
        audio_level = audioop.rms(data, 2)
        frames.append(data)

        # Vérifier le niveau sonore pour arrêter l'enregistrement
        if audio_level < THRESHOLD:
            silence_count += 1
        else:
            silence_count = 0

        # Arrêter l'enregistrement après 2 secondes de silence
        if silence_count > (SILENCE_LIMIT * RATE / CHUNK) or started_recording > (5 * RATE / CHUNK):
            print("Silence détecté, arrêt de l'enregistrement...")
            break
        started_recording+=1
    print("Fin de l'enregistrement...")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": transcription.text}
    ]
    )
    print(response.choices[0].message.content)
    dt.text_2_speech(response.choices[0].message.content, engine="aplay")


def listen_for_keyword():


    base_model = Resnet50_Arc_loss()

    mycroft_hw = HotwordDetector(
        hotword="jarvis",
        model = base_model,
        reference_file="/home/theo/jarvis/EfficientWordNet/EfficientWord-Net/wakewords/jarvis/jarvis_ref.json",
        threshold=0.7,
        relaxation_time=2
    )

    mic_stream = SimpleMicStream(
        window_length_secs=1.5,
        sliding_window_secs=0.75,
    )

    mic_stream.start_stream()

    print("Say jarvis ")
    while True :
        frame = mic_stream.getFrame()
        result = mycroft_hw.scoreFrame(frame)
        if result==None :
            #no voice activity
            continue
        if(result["match"]):
            print("Wakeword uttered",result["confidence"])
            result = speech_to_text()
            print(result)

if __name__ == '__main__':
    detected = listen_for_keyword()
