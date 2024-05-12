from pydub import AudioSegment
from pydub.playback import play

def adjust_audio_length(audio_path, target_length_ms=1500):
    # Charger le fichier audio
    audio = AudioSegment.from_file(audio_path)
    
    # Calculer la durée actuelle en millisecondes
    current_length_ms = len(audio)
    
    if current_length_ms > target_length_ms:
        # Couper l'audio si plus long que la durée cible
        audio = audio[:target_length_ms]
    elif current_length_ms < target_length_ms:
        # Ajouter du silence si l'audio est plus court que la durée cible
        silence_duration = target_length_ms - current_length_ms
        silence = AudioSegment.silent(duration=silence_duration)
        audio += silence  # Concaténer l'audio avec le silence
    
    return audio

# Utiliser la fonction
adjusted_audio = adjust_audio_length("/home/theo/jarvis/EfficientWordNet/EfficientWord-Net/wakewords/jarvis/jarvis_fr-FR_theo_mp3-to.wav")
play(adjusted_audio)  # Jouer l'audio ajusté
