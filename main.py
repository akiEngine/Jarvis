import pyaudio
import wave
import openai
from openai import OpenAI
import audioop
import os
import vlc
import paho.mqtt.client as mqtt
import pvporcupine
import struct
from pvrecorder import PvRecorder
from datetime import datetime
import argparse

'''
# Configuration du client MQTT
broker = "mqtt.example.com"
port = 1883
topic = "test/topic"
message = "Hello, MQTT!"
username = "your_username"
password = "your_password"

mqtt_client = mqtt.Client()

mqtt_client.username_pw_set(username, password)

mqtt_client.connect(broker, port)

mqtt_client.publish(topic, message)

'''
# AccessKey obtained from Picovoice Console (https://console.picovoice.ai/)
PP_access_key = os.getenv("PORCUPINE_API")

# Paths to keyword file and model file
keyword_paths = ['porcupine/Jarre-vis_fr_linux_v3_0_0.ppn']
model_path = "porcupine/porcupine_params_fr.pv"
keywords = ["Jarre vis"]  # Liste de mots-clés à détecter
sensitivities = [0.5] * len(keyword_paths)

  # Create Porcupine handle
porcupine = pvporcupine.create(
    access_key=PP_access_key,
    keyword_paths=keyword_paths,
    model_path=model_path,
    keywords = ['Jarre vis'],
    sensitivities=sensitivities
)
keywords = [os.path.basename(x).replace('.ppn', '').split('_')[0] for x in keyword_paths]
print('Porcupine version: %s' % porcupine.version)
recorder = PvRecorder(frame_length=porcupine.frame_length, device_index=-1)


client = OpenAI()

messages=[
    {"role": "system", "content": "tu es mon assistant personel, tu es enjoué, peut improviser et donner des anecdotes, tu réponds à mes questions et gère ma domotique."},
    {"role": "user", "content": "Sois conçis."}
]

def pre_compute(text):
    to_return = True

    return to_return


def speech_to_text():
    API_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = API_KEY
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = "output.wav"
    THRESHOLD = 300  # level to start recording
    SILENCE_LIMIT = 1.5  # time of silence before stoping recording
    silence_count = 0

    audio = pyaudio.PyAudio()

    print("Init de l'enregistrement...")

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []
    
    # Detect the audio level before recording
    data = stream.read(CHUNK)
    audio_level = audioop.rms(data, 2)
    started_recording = 0

    # recording of the audio
    while True:
        data = stream.read(CHUNK)
        audio_level = audioop.rms(data, 2)
        frames.append(data)

        # check noise level to stop recording
        if audio_level < THRESHOLD:
            silence_count += 1
        else:
            silence_count = 0

        # stop recording if 2s silence
        if silence_count > (SILENCE_LIMIT * RATE / CHUNK) or started_recording > (5 * RATE / CHUNK):
            print("Silence detected...")
            break
        started_recording+=1
    print("end of recording...")

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
    if len(transcription.text) >3 and pre_compute(transcription.text):
        messages[1] = {"role": "user", "content": transcription.text+" Sois conçis."}
        response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
        )
        output = response.choices[0].message.content
        print(output)
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=output,
        )

        with open("outputtts.mp3", "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)

        os.system("ffplay -v 0 -nodisp -autoexit outputtts.mp3") 


def listen_for_keyword():


    recorder.start()


    print('Listening ... (press Ctrl+C to exit)')

    try:
        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)
            if result >= 0:
                print('[%s] Detected %s' % (str(datetime.now()), keywords[result]))
                result = speech_to_text()
                print(result)
    except KeyboardInterrupt:
        print('Stopping ...')
    finally:
        recorder.delete()
        porcupine.delete()



if __name__ == '__main__':
    try:
        detected = listen_for_keyword()
    finally:
        # Déconnexion du client
        mqtt_client.disconnect()
    
