---
license: mit
language:
- es
- en
- zh
- fr
- pt
pipeline_tag: text-generation
tags:
- nova-2b
- modernotech
- nova-ai
- custom-architecture
- conversational
- uncensored
- 1m-context
model_name: Nova 2B (Nova AI)
model_creator: ModernoTech
widget: []
inference: false
---



# Nova AI — Arquitectura Híbrida Oficial (ModernoTech)


[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Format](https://img.shields.io/badge/Format-GGUF%20v3-green.svg)](docs/NOVA_GGUF_SPEC.md)
[![Architecture](https://img.shields.io/badge/Architecture-Hybrid%20MoCE%20%2B%20Ternary%20Native-orange.svg)](#arquitectura-técnica)
[![Context Window](https://img.shields.io/badge/Context%20Window-1M%20Tokens-purple.svg)](#especificaciones-técnicas)

**Nova AI** es una inteligencia artificial conversacional e híbrida desarrollada por **ModernoTech**, concebida para ser **ultrapotente en relación con su tamaño, ultracompacta, ultraligera y con arquitectura de auto-mejora continua**.

---

## 💡 Concepto Fundamental

Nova AI rompe la dependencia absoluta de los LLMs gigantes. En su lugar, distribuye la inteligencia en tres pilares:

```text
                                  NOVA AI
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
             [ NOVA NATIVE ]                   [ NOVA 2B LLM ]
       100% Integer & Ternary {-1,0,1}      Inferencia GGUF Universal
                    │                       (LM Studio, Ollama, llama.cpp)
     ┌──────────────┼──────────────┐
     ▼              ▼              ▼
 [MoCE Experts] [User Memory] [Nova RAG FTS5]
                    │
                    ▼
        [Self-Improvement Engine]
```

1. **Nova Native (100% Entero y Ternario):** Computación en pesos ternarios empaquetados (2 bits por peso) con acumuladores `Int32` y activaciones `Int16`. Cero uso de `float` en operaciones críticas.
2. **Mixture of Code-Experts (MoCE):** Expertos modulares en Python con conocimiento estructurado persistente en SQLite (`storage/knowledge.db`):
   - **`CodeExpert`**: HTML5, CSS3, JavaScript, Python.
   - **`LanguagesExpert`**: Chino Mandarín, Inglés, Francés, Portugués, Español.
   - **`MathExpert`**: Álgebra lineal, cálculo, probabilidad y lógica.
3. **RAG Ultraligero SQLite FTS5:** Búsqueda léxica con ranking BM25 sin necesidad de bases vectoriales pesadas.
4. **Self-Improvement Engine:** Detecta debilidades, autopsia de errores, genera ejercicios sintéticos de práctica, verifica resultados y consolida mejoras en disco de forma autónoma.
5. **Nova 2B LLM (GGUF):** Actúa como motor de razonamiento de respaldo y profesor para sintetizar conocimiento nuevo.

---

## 🚀 Despliegue Rápido

### Opción 1: Modelo GGUF Universal (LM Studio / Ollama / llama.cpp)
El archivo `nova-2b.gguf` puede ejecutarse directamente en cualquier cliente compatible con GGUF desde el Hugging Face Hub:
- **LM Studio:** Buscar **`ModernoTech/nova-2b`** y presionar **Download**.
- **Ollama:**
  ```bash
  ollama run hf.co/ModernoTech/nova-2b
  ```
- **llama.cpp:**
  ```bash
  ./llama-server -hf ModernoTech/nova-2b -c 1048576 --temp 0.8 --top-p 0.95
  ```


### Opción 2: Nova AI Framework Completo (MoCE + RAG + Auto-Mejora)
Ejecuta la consola interactiva con todas las capas activadas:
```bash
python3 nova_core.py
```
- Escribe preguntas técnicas o habla cotidianamente.
- Para enseñar: `Aprende esto: <hecho nuevo>`
- Para forzar auto-mejora: `/improve`
- Para ver rendimiento por habilidad: `/skills`
- Para ver estadísticas: `/stats`

### Opción 3: Servidor API Compatible con OpenAI
Levanta el endpoint HTTP local en el puerto 8080:
```bash
python3 nova_server.py
```
- **Endpoint:** `http://127.0.0.1:8080/v1/chat/completions` (compatible con Open WebUI, Cursor, VS Code).
- **Estado:** `http://127.0.0.1:8080/status`

---

## 🧪 Auditorías y Pruebas Unitarias

Nova AI cuenta con un riguroso sistema de pruebas y auditoría automática:

```bash
# 1. Auditoría estricta Integer-Only / Ternary (falla si detecta float):
python3 nova_auditor.py

# 2. Suite de pruebas unitarias completas:
python3 -m unittest tests/test_nova_suite.py
```

---

## 📄 Especificación de Metadatos
Para consultar el estándar de metadatos propios de Nova incrustados en GGUF, revisa [docs/NOVA_GGUF_SPEC.md](docs/NOVA_GGUF_SPEC.md).

---

## 📜 Licencia y Autoría

Copyright (c) 2026 **ModernoTech / José Luis Brea**.  
Distribuido bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
