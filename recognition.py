import os
from pocketsphinx import LiveSpeech, get_model_path

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
        print("Démarrage de l'enregistrement ou d'autres actions...")
