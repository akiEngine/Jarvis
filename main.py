import pyaudio
import wave
import openai
import audioop
import time
import os
from pocketsphinx import LiveSpeech, get_model_path

def speech_to_text():
    API_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = API_KEY
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = "output.wav"
    THRESHOLD = 300  # Niveau pour démarrer l'enregistrement
    SILENCE_LIMIT = 2  # Temps de silence avant d'arrêter l'enregistrement (en secondes)
    silence_count = 0

    audio = pyaudio.PyAudio()

    print("Initialisation de l'enregistrement...")

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []
    
    # Détecter le niveau sonore avant de commencer à enregistrer
    print("En attente de parole...")
    data = stream.read(CHUNK)
    audio_level = audioop.rms(data, 2)


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
        if silence_count > (SILENCE_LIMIT * RATE / CHUNK):
            print("Silence détecté, arrêt de l'enregistrement...")
            break

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
        print(transcription.text)



def listen_for_keyword():
    model_path = "/home/theo/.local/lib/python3.10/site-packages/pocketsphinx/model/en-us/"

    speech = LiveSpeech(
        verbose=False,
        sampling_rate=16000,
        buffer_size=2048,
        no_search=False,
        full_utt=False,
        hmm=os.path.join(model_path, 'en-us/'),  # Ajuster selon le vrai chemin
        lm=False,
        dic=os.path.join(model_path, 'cmudict-en-us.dict'),
        kws=os.path.join(model_path, 'keywords.list')
    )

    print("En écoute pour le mot-clé 'Jarvis'...")

    for phrase in speech:
        for segment in phrase.seg():
            print(segment.word)
            if segment.word.lower() == 'jarvis':
                print("Mot-clé 'Jarvis' détecté !")
                return True
    return False

if __name__ == '__main__':
    detected = listen_for_keyword()
    if detected:
        speech_to_text()
