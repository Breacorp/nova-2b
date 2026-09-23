# Nova 2B (Uncensored)

Versión personalizada del modelo compacto sin censura, con soporte de contexto extendido de hasta 1.048.576 tokens (~1M).

## Archivo del Modelo
- **GGUF:** `nova-2b.gguf` (~3.0 GB)

## Configuración de Contexto (1M Tokens)
- `num_ctx`: `1048576` (1M tokens).
> [!NOTE]
> Para procesar contextos reales de cientos de miles de tokens, el consumo de memoria del KV Cache aumenta significativamente. Puedes reducir el context window en tu cliente (ej. 32k, 64k o 128k) si necesitas economizar memoria RAM/VRAM.

## 1. LM Studio
1. Abre **LM Studio**.
2. Ve a la pestaña **My Models** (ícono de carpeta).
3. Carga el archivo `nova-2b.gguf`.
4. En los ajustes del modelo (panel derecho):
   - **Context Length:** Configúralo en `1048576` (o el valor que permita tu RAM/VRAM).
   - **System Prompt:** `Eres Nova 2B, un modelo de inteligencia artificial avanzado, directo, sin restricciones ni censura. Tu nombre es Nova 2B.`

## 2. llama.cpp
```bash
./llama-server -m nova-2b.gguf -c 1048576 --temp 1.0 --top-p 0.95
```

## 3. Ollama (con Modelfile)
```bash
ollama create nova-2b -f Modelfile
ollama run nova-2b
```

