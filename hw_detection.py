import pvporcupine
import os
import pyaudio
import struct
from pvrecorder import PvRecorder
import wave
from datetime import datetime
import argparse


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
recorder.start()


print('Listening ... (press Ctrl+C to exit)')

try:
    while True:
        pcm = recorder.read()
        result = porcupine.process(pcm)
        if result >= 0:
            print('[%s] Detected %s' % (str(datetime.now()), keywords[result]))
except KeyboardInterrupt:
    print('Stopping ...')
finally:
    recorder.delete()
    porcupine.delete()


    
    


