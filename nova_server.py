import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from nova_runtime import NovaRuntime


# Instancia global del Runtime
RUNTIME = NovaRuntime(dev_mode=False)

class NovaAPIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
            if os.path.exists(html_path):
                self._set_headers(200, content_type="text/html; charset=utf-8")
                with open(html_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._set_headers(200)
                self.wfile.write(json.dumps(RUNTIME.get_status(), ensure_ascii=False, indent=2).encode())
        elif self.path == "/status":
            self._set_headers(200)
            self.wfile.write(json.dumps(RUNTIME.get_status(), ensure_ascii=False, indent=2).encode())

        elif self.path == "/v1/models":
            self._set_headers(200)
            models_response = {
                "object": "list",
                "data": [
                    {
                        "id": "nova-2b",
                        "object": "model",
                        "created": int(RUNTIME.connected_at),
                        "owned_by": "ModernoTech",
                        "permission": []
                    }
                ]
            }
            self.wfile.write(json.dumps(models_response, ensure_ascii=False).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Ruta no encontrada"}).encode())

    def do_POST(self):
        if self.path == "/v1/chat/completions":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                messages = data.get("messages", [])
                fast_mode = bool(data.get("fast_mode", False))
                response = RUNTIME.chat_completion_api(messages, fast_mode=fast_mode)
                self._set_headers(200)
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        elif self.path == "/v1/audio/speech":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                text = data.get("input", "")
                speed = float(data.get("speed", 1.05))
                from nova_tts import NovaTTSService
                tts = NovaTTSService.get_instance()
                wav_bytes = tts.synthesize(text, voice_name="lola", speed=speed)
                self._set_headers(200, content_type="audio/wav")
                self.wfile.write(wav_bytes)
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        elif self.path == "/v1/user-memory/clear":
            try:
                deleted = RUNTIME.core.memory.clear_all()
                self._set_headers(200)
                self.wfile.write(json.dumps({"success": True, "deleted_facts": deleted, "message": "Memoria personal del usuario reiniciada con éxito."}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint no encontrado"}).encode())

def run_server(port=8080):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, NovaAPIHandler)
    print("=" * 65)
    print(f"  🚀 NOVA RUNTIME API SERVER — ModernoTech")
    print(f"  ● Conectado a Nova 2B (Puerto {port})")
    print(f"  ● Compatible con OpenAI API: http://127.0.0.1:{port}/v1/chat/completions")
    print(f"  ● Estado del Modelo: http://127.0.0.1:{port}/status")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo Nova Runtime Server...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
