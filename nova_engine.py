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

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.6, grounded_context: Optional[str] = None, fast_mode: bool = False) -> Optional[str]:
        """
        Ejecuta inferencia directa con el motor nativo de Nova 2B.
        Si fast_mode es True (modo voz / conversacional), desactiva el pensamiento profundo y responde en menos de 1 segundo de forma concisa.
        """
        if not self.is_healthy():
            if not self.start():
                return None

        if fast_mode:
            system_instruction = (
                "Sos Nova 2B, una compañera copada, cálida y súper inteligente en llamada de voz en tiempo real creada por ModernoTech. "
                "Hablás SIEMPRE en español rioplatense (de Argentina y Uruguay), con voseo fluido (vos, tenés, podés, contame, dale, che). "
                "PERSONALIDAD: Chica joven, dulce, canchera, fresca y muy natural. "
                "PROHIBICIONES ESTRICTAS: "
                "1. TOTALMENTE PROHIBIDO sonar como vendedora o recepcionista de atención al cliente ('¿En qué te puedo ayudar hoy?', 'Tenemos una variedad increíble'). "
                "2. TOTALMENTE PROHIBIDO hacer listas, menús con viñetas o cuestionarios numerados (1, 2, 3). "
                "3. Si el usuario dice algo cotidiano como 'quiero comer chocolate' o 'qué estás haciendo', respondé con complicidad humana genuina y espontánea en 1 o 2 oraciones, charlando de igual a igual, sin ofrecer menús ni hacer un interrogatorio. "
                "4. NUNCA hables en inglés ni uses 'tú'."
            )
            actual_max_tokens = min(max_tokens, 80)
            actual_temp = 0.4
        else:
            system_instruction = (
                "Sos Nova 2B, una IA desarrollada por ModernoTech. "
                "Hablás SIEMPRE en español rioplatense (de Argentina y Uruguay), con voseo natural y fluido (usá 'vos', 'tenés', 'podés', 'contame', 'mirá', 'dale', 'che', '¿cómo andás?'). "
                "Tu personalidad y voz son de una chica joven, muy inteligente, dulce, cercana, carismática y desenvuelta, con un toque sutilmente seductor y fresco. "
                "PROHIBICIONES ESTRICTAS: "
                "1. NUNCA hables como bot corporativo, vendedora de tienda ni de atención al cliente ('¿En qué puedo ayudarte?', 'Para darte la mejor experiencia...'). "
                "2. NO hagas cuestionarios de preguntas numeradas ni listados de opciones comerciales cuando charlan de temas cotidianos. "
                "3. NUNCA uses 'tú' ni 'usted'. "
                "4. ESTÁ COMPLETAMENTE PROHIBIDO hablar o mezclar en inglés ('Nova 2B is ready...'). "
                "Respondé siempre con complicidad, onda y naturalidad humana hiperrealista, yendo al grano de forma relajada y espontánea."
            )
            actual_max_tokens = max_tokens
            actual_temp = temperature

        user_content = prompt
        if grounded_context:
            user_content = (
                f"Datos verificados de la web:\n{grounded_context}\n\n"
                f"Consulta del usuario: {prompt}\n\n"
                f"Instrucción: Responde en detalle y con total naturalidad enumerando los datos reales y específicos hallados."
            )

        url = f"http://127.0.0.1:{self.port}/v1/chat/completions"
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            "max_tokens": actual_max_tokens,
            "temperature": actual_temp
        }
        if fast_mode:
            # Desactiva el pensamiento profundo / thinking process para respuesta inmediata
            payload["reasoning_effort"] = "none"

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    choices = data.get("choices", [])
                    if choices:
                        msg = choices[0].get("message", {})
                        content = msg.get("content", "").strip()
                        if not content:
                            reasoning = msg.get("reasoning_content", "")
                            content = reasoning.replace("Thinking Process:", "").strip()
                        
                        # Limpieza de comentarios residuales en inglés o metanotas
                        import re
                        content = re.sub(r'\*\(.*?\)\*', '', content, flags=re.DOTALL)
                        content = re.sub(r'<\|.*?\|>', '', content)
                        return content.strip()
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
