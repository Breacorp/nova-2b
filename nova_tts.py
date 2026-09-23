"""
NOVA TTS SERVICE (Kokoro ONNX Engine + Voice Cloning)
Provee síntesis de voz natural, hiperrealista y ultrarrápida (latencia < 0.15s).
Soporta voces nativas y perfiles de voz clonados (Lola, etc.).
"""

import io
import os
import time
import zipfile
import numpy as np
import soundfile as sf
from typing import Optional, Union
from kokoro_onnx import Kokoro

os.environ["ESPEAK_DATA_PATH"] = "/opt/homebrew/share/espeak-ng-data"
os.environ["PHONEMIZER_ESPEAK_PATH"] = "/opt/homebrew/bin/espeak-ng"

MODEL_PATH = "models/tts/kokoro-v1.0.onnx"
VOICES_BIN = "models/tts/voices-v1.0.bin"
CLONES_DIR = "storage/voice_clones"

class NovaTTSService:
    _instance = None

    def __init__(self):
        if not os.path.exists(MODEL_PATH) or not os.path.exists(VOICES_BIN):
            raise FileNotFoundError("Kokoro ONNX model files not found in models/tts/")
        
        self.kokoro = Kokoro(MODEL_PATH, VOICES_BIN)
        self.cached_clones = {}
        self._load_clones()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_clones(self):
        os.makedirs(CLONES_DIR, exist_ok=True)
        for fname in os.listdir(CLONES_DIR):
            if fname.endswith(".npy"):
                name = fname[:-4]
                path = os.path.join(CLONES_DIR, fname)
                try:
                    self.cached_clones[name] = np.load(path)
                except Exception as e:
                    print(f"[TTS] Error loading clone {name}: {e}")

    def synthesize(self, text: str, voice_name: str = "lola", speed: float = 1.05) -> bytes:
        """
        Sintetiza texto a audio WAV en formato bytes.
        """
        start = time.time()
        
        # 1. Determinar embedding de voz
        voice_target: Union[str, np.ndarray] = voice_name
        if voice_name in self.cached_clones:
            voice_target = self.cached_clones[voice_name]
        elif voice_name == "lola":
            # Si no está en caché, intentar cargarlo o crear fallback
            lola_path = os.path.join(CLONES_DIR, "lola.npy")
            if os.path.exists(lola_path):
                self.cached_clones["lola"] = np.load(lola_path)
                voice_target = self.cached_clones["lola"]
            else:
                voice_target = "ef_dora"

        # 2. Generar muestras de audio con Kokoro ONNX
        samples, sample_rate = self.kokoro.create(
            text,
            voice=voice_target,
            speed=speed,
            lang="es"
        )

        # 3. Exportar a buffer WAV en memoria
        buffer = io.BytesIO()
        sf.write(buffer, samples, sample_rate, format="WAV")
        buffer.seek(0)
        
        elapsed = time.time() - start
        audio_dur = len(samples) / sample_rate
        print(f"[TTS] Sintetizado: {len(text)} chars -> {audio_dur:.2f}s audio en {elapsed:.3f}s (RTF: {elapsed/max(audio_dur, 0.01):.2f})")
        return buffer.read()

if __name__ == "__main__":
    service = NovaTTSService.get_instance()
    wav = service.synthesize("Hola José Luis, la integración del motor de voz natural está completa.", "lola")
    print(f"Generados {len(wav)} bytes de audio.")
