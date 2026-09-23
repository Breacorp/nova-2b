"""
NOVA TTS SERVICE (Coqui XTTS v2 — Clonación Cero-Muestra en Español Nativo)
Sintetiza audio replicando fielmente el timbre de voice-lola.mp3
con pronunciación española nativa perfecta, sin ruidos ni balbuceos.
"""

import io
import os
import time
import threading
import soundfile as sf
import torch

# Parche PyTorch 2.6 para carga confiable de checkpoints de Coqui
_orig_load = torch.load
def _custom_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _orig_load(*args, **kwargs)
torch.load = _custom_load

os.environ["COQUI_TOS_AGREED"] = "1"
from TTS.api import TTS

REF_AUDIO = "voices/voice-lola-reference.wav"
_tts_lock = threading.Lock()

class NovaTTSService:
    _instance = None

    def __init__(self):
        print("[TTS] Inicializando motor Coqui XTTS v2 para español...")
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        print("[TTS] XTTS v2 listo para clonación.")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def synthesize(self, text: str, voice_name: str = "lola", speed: float = 1.0) -> bytes:
        start = time.time()
        output_temp = f"/tmp/nova_xtts_{int(time.time()*1000)}.wav"
        
        with _tts_lock:
            self.tts.tts_to_file(
                text=text,
                speaker_wav=REF_AUDIO,
                language="es",
                file_path=output_temp
            )
            
        with open(output_temp, "rb") as f:
            wav_bytes = f.read()
            
        try:
            os.remove(output_temp)
        except OSError:
            pass
            
        elapsed = time.time() - start
        print(f"[XTTS-v2] Sintetizado '{text[:30]}...' en {elapsed:.2f}s")
        return wav_bytes

if __name__ == "__main__":
    tts = NovaTTSService.get_instance()
    wav = tts.synthesize("Hola, prueba de síntesis con XTTS v2 y la voz de Lola.")
    print(f"Generados {len(wav)} bytes.")
