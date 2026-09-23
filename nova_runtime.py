import os
import json
import time
from typing import Dict, Any, List, Optional
from nova_core import NovaCore

class NovaRuntime:
    """
    Nova Runtime — Capa de abstracción y ejecución unificada de Nova AI.
    Desarrollado por ModernoTech.

    Oculta toda la complejidad interna (MoCE, RAG FTS5, Memory, Learning,
    Ternary Native y LLM) bajo una experiencia única de 'Modelo Conectado'.
    """
    def __init__(self, model_path: Optional[str] = None, dev_mode: bool = False):
        self.dev_mode = dev_mode
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = model_path or os.path.join(self.base_dir, "nova-2b.gguf")
        
        # 1. Cargar metadatos del paquete
        self.manifest = self._load_manifest()
        
        # 2. Inicializar núcleo completo
        self.core = NovaCore()
        self.is_connected = True
        self.connected_at = time.time()

    def _load_manifest(self) -> Dict[str, Any]:
        preset_file = os.path.join(self.base_dir, "model_preset.json")
        if os.path.exists(preset_file):
            with open(preset_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "name": "Nova 2B",
            "displayName": "Nova 2B by ModernoTech",
            "contextWindow": 1048576,
            "architecture": "nova-hybrid"
        }

    def get_status(self) -> Dict[str, Any]:
        """Estado limpio visible para el usuario o interfaz."""
        return {
            "model": self.manifest.get("name", "Nova 2B"),
            "display_name": self.manifest.get("displayName", "Nova 2B by ModernoTech"),
            "status": "Connected" if self.is_connected else "Disconnected",
            "context_window": self.manifest.get("contextWindow", 1048576),
            "backend": "Nova Native + GGUF Engine",
            "uptime_seconds": int(time.time() - self.connected_at) if self.is_connected else 0
        }

    def chat(self, prompt: str, fast_mode: bool = False) -> str:
        """
        Punto de entrada simple para el usuario final.
        Devuelve únicamente el texto de respuesta sin metadatos técnicos.
        """
        start_t = time.time()
        result = self.core.ask(prompt, fast_mode=fast_mode)
        latency_ms = int((time.time() - start_t) * 1000)

        clean_response = result["response"]
        
        # En modo desarrollador, adjunta telemetría
        if self.dev_mode:
            telemetry = (
                f"\n\n[DevMode Telemetry: Layer='{result.get('layer', 'Unknown')}' | "
                f"Action='{result.get('action', 'direct')}' | Latency={latency_ms}ms]"
            )
            return clean_response + telemetry

        return clean_response

    def chat_completion_api(self, messages: List[Dict[str, str]], fast_mode: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Endpoint compatible con el estándar OpenAI (POST /v1/chat/completions).
        Permite conectar Open WebUI, LM Studio, Cursor, VS Code, etc.
        """
        user_message = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_message = m.get("content", "")
                break

        start_t = time.time()
        reply_content = self.chat(user_message, fast_mode=fast_mode)
        latency_ms = int((time.time() - start_t) * 1000)

        return {
            "id": f"chatcmpl-nova-{int(time.time()*1000)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": self.manifest.get("name", "nova-2b"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": reply_content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(reply_content.split()),
                "total_tokens": len(user_message.split()) + len(reply_content.split())
            },
            "nova_telemetry": {
                "latency_ms": latency_ms,
                "engine": "Nova Native Hybrid"
            } if self.dev_mode else None
        }
