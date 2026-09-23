#!/usr/bin/env python3
"""
Nova Native Engine Manager — ModernoTech
Administra el proceso del motor de inferencia nativo de Nova 2B (bin/nova-engine).
Carga directamente el binario './nova-2b.gguf' sin depender de Ollama, LM Studio ni servicios externos.
"""

import os
import sys
import time
import json
import socket
import subprocess
import urllib.request
from typing import Optional, Dict, Any

class NovaEngineManager:
    def __init__(self, port: int = 11435, ctx_size: int = 4096, n_gpu_layers: int = 99):
        self.port = port
        self.ctx_size = ctx_size
        self.n_gpu_layers = n_gpu_layers
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.bin_path = os.path.join(self.base_dir, "bin", "nova-engine")
        self.model_path = os.path.join(self.base_dir, "nova-2b.gguf")
        self.process: Optional[subprocess.Popen] = None

    def is_port_in_use(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", self.port)) == 0

    def is_healthy(self) -> bool:
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{self.port}/health")
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read().decode())
                return data.get("status") == "ok"
        except Exception:
            return False

    def start(self, timeout_sec: int = 25) -> bool:
        if self.is_healthy():
            return True

        if not os.path.exists(self.bin_path):
            raise FileNotFoundError(f"Motor nativo no encontrado en: {self.bin_path}")

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Archivo de modelo GGUF no encontrado en: {self.model_path}")

        cmd = [
            self.bin_path,
            "-m", self.model_path,
            "--port", str(self.port),
            "-c", str(self.ctx_size),
            "-ngl", str(self.n_gpu_layers),
            "--host", "127.0.0.1"
        ]

        # Iniciar en segundo plano
        log_file = open(os.path.join(self.base_dir, "storage", "nova_engine.log"), "a", encoding="utf-8")
        self.process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=log_file,
            cwd=self.base_dir
        )

        start_t = time.time()
        while time.time() - start_t < timeout_sec:
            if self.is_healthy():
                return True
            time.sleep(0.5)

        return False

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Optional[str]:
        """
        Ejecuta inferencia directa con el motor nativo de Nova 2B.
        """
        if not self.is_healthy():
            if not self.start():
                return None

        url = f"http://127.0.0.1:{self.port}/v1/chat/completions"
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Eres Nova 2B, la inteligencia artificial avanzada desarrollada por ModernoTech. Responde siempre de forma clara, directa, profesional y sin mostrar procesos internos de razonamiento ni comentarios en etiquetas."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    choices = data.get("choices", [])
                    if choices:
                        msg = choices[0].get("message", {})
                        content = msg.get("content", "").strip()
                        # Si el contenido está vacío pero hay reasoning, o viene con tags, limpiar
                        if not content:
                            reasoning = msg.get("reasoning_content", "")
                            # Si solo devolvió razonamiento por max_tokens, usar el razonamiento limpio o mensaje directo
                            content = reasoning.replace("Thinking Process:", "").strip()
                        return content
        except Exception as e:
            return None

        return None

    def stop(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except Exception:
                if self.process:
                    self.process.kill()
