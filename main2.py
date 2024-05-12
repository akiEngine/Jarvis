import pyaudio
import wave
import openai
import os
from collections import deque
import audioop
import time

def continuous_listen():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    THRESHOLD = 300  # Niveau pour démarrer l'enregistrement
    BUFFER_MAX_LENGTH = 5 * RATE  # 5 secondes de buffer
    BUFFER_SLIDING_WINDOW = 1 * RATE  # Fenêtre glissante de 1 seconde

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Listening continuously...")

    audio_buffer = deque(maxlen=BUFFER_MAX_LENGTH // CHUNK)  # Création d'un buffer circulaire

    try:
        while True:
            data = stream.read(CHUNK)
            audio_buffer.append(data)
            audio_level = audioop.rms(data, 2)
            
            # Ici, vous intégreriez votre détection de mot-clé
            # Exemple simplifié de détection de mot-clé:
            if audio_level > THRESHOLD:
                print("Keyword detected")
                # Traiter le buffer pour la transcription ou autre traitement
                # Éventuellement, sauvegarder le buffer actuel dans un fichier
                save_buffer(audio_buffer, audio, CHANNELS, FORMAT, RATE)

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

def save_buffer(audio_buffer, audio, channels, FORMAT, RATE):
    print("Saving buffer...")
    wf = wave.open('output.wav', 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(list(audio_buffer)))
    wf.close()
    print("Buffer saved")

if __name__ == '__main__':
    continuous_listen()
