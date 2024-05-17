import pyaudio
import wave
import openai
from openai import OpenAI
import audioop
import os
from eff_word_net.streams import SimpleMicStream
from eff_word_net.engine import HotwordDetector
from eff_word_net.audio_processing import Resnet50_Arc_loss
import vlc


client = OpenAI()

messages=[
    {"role": "system", "content": "tu es mon assistant personel, tu es enjoué, peut improviser et donner des anecdotes, tu réponds à mes questions et gère ma domotique."},
    {"role": "user", "content": "Sois conçis."}
]


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
    
    # Ddetect the audio level before recording
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
    if len(transcription.text)  >3:
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


    base_model = Resnet50_Arc_loss()

    mycroft_hw = HotwordDetector(
        hotword="jarvis",
        model = base_model,
        reference_file="/home/theo/jarvis/EfficientWordNet/EfficientWord-Net/wakewords/jarvis/jarvis_ref.json",
        threshold=0.69,
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
