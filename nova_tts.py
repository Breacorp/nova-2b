"""
NOVA TTS SERVICE (Motor F5-TTS con clonación cero-muestra idéntica)
Utiliza directamente la muestra de audio de referencia voice-lola.mp3
para sintetizar frases con el timbre, aire, respiración y prosodia EXACTOS.
"""

import io
import os
import time
import threading
import soundfile as sf
import torch
from huggingface_hub import hf_hub_download
from f5_tts.infer.utils_infer import load_model, load_vocoder, infer_process
from f5_tts.model import DiT

_tts_lock = threading.Lock()

REF_AUDIO = "voices/voice-lola-reference.wav"
REF_TEXT = "Nada, que anoche a las tres empieza a pitar el detector de humo, a las tres, y yo en pelotas, subido a una silla dándole al botoncito ese que no hace nada."

class NovaTTSService:
    _instance = None

    def __init__(self):
        print("[TTS] Inicializando F5-TTS con pesos oficiales DiT...")
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        
        # Vocoder
        self.vocoder = load_vocoder(is_local=False)
        
        # Modelo DiT F5-TTS
        ckpt_path = hf_hub_download(repo_id="SWivid/F5-TTS", filename="F5TTS_Base/model_1200000.safetensors")
        model_cls = DiT
        model_cfg = dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4)
        self.ema_model = load_model(model_cls, model_cfg, ckpt_path=ckpt_path, device=self.device)
        print(f"[TTS] F5-TTS listo en dispositivo: {self.device}")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def synthesize(self, text: str, voice_name: str = "lola", speed: float = 1.0) -> bytes:
        """
        Sintetiza la frase clonando con fidelidad total la voz de Lola
        """
        start = time.time()
        
        with _tts_lock:
            if torch.backends.mps.is_available():
                torch.mps.synchronize()

            audio, final_sample_rate, _ = infer_process(
                REF_AUDIO,
                REF_TEXT,
                text,
                self.ema_model,
                self.vocoder,
                mel_spec_type="vocos",
                target_rms=0.1,
                cross_fade_duration=0.15,
                nfe_step=16,
                cfg_strength=2.0,
                speed=speed,
                device=self.device
            )

            if torch.backends.mps.is_available():
                torch.mps.synchronize()

        buffer = io.BytesIO()
        sf.write(buffer, audio, final_sample_rate, format="WAV")
        buffer.seek(0)
        
        elapsed = time.time() - start
        audio_dur = len(audio) / final_sample_rate
        print(f"[F5-TTS] Sintetizado '{text[:30]}...' -> {audio_dur:.2f}s en {elapsed:.2f}s")
        return buffer.read()

if __name__ == "__main__":
    tts = NovaTTSService.get_instance()
    wav = tts.synthesize("Hola, prueba de síntesis directa con la voz de Lola.")
    print(f"Generados {len(wav)} bytes.")
