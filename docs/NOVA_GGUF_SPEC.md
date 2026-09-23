# Especificación de Metadatos GGUF — Nova AI
# Desarrollado por ModernoTech

Esta especificación define el estándar de metadatos propios de Nova incrustados dentro del encabezado GGUF.
Los runtimes genéricos (LM Studio, llama.cpp, Ollama) ignoran las claves desconocidas y ejecutan el modelo con normalidad;
mientras que Nova Framework las interpreta para activar capacidades extendidas (MoCE, RAG, Self-Improvement y Memoria).

---

## 1. Tabla de Claves de Metadatos (Namespace `nova.*`)

| Clave GGUF | Tipo GGUF | Valor Ejemplo | Descripción |
|---|---|---|---|
| `nova.version` | `STRING` | `"2.0.0"` | Versión del estándar de metadatos Nova. |
| `nova.family` | `STRING` | `"nova-hybrid"` | Familia de modelo híbrido ModernoTech. |
| `nova.author` | `STRING` | `"ModernoTech"` | Autor y propietario tecnológico. |
| `nova.experts` | `ARRAY[STRING]` | `["code", "languages", "math"]` | Expertos MoCE compatibles para este modelo. |
| `nova.reasoning` | `STRING` | `"hybrid-moce"` | Modo de razonamiento (híbrido determinista + LLM). |
| `nova.ternary_ready` | `BOOL` | `true` | Indica soporte para el motor entero/ternario empaquetado. |
| `nova.rag_supported` | `BOOL` | `true` | Soporta inyección de contexto RAG FTS5. |
| `nova.self_improve` | `BOOL` | `true` | Habilita bucle autónomo de detección de brechas y práctica. |
| `nova.context_window` | `UINT32` | `1048576` | Ventana de contexto extendida nativa (1M tokens). |
| `nova.recommended_temp`| `FLOAT32` | `0.8` | Temperatura óptima para razonamiento. |
| `nova.recommended_top_p`| `FLOAT32`| `0.95` | Top_p recomendado. |

---

## 2. Comportamiento Multi-Plataforma

```text
                        Nova-2B.gguf
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   [ RUNTIMES ESTÁNDAR ]              [ NOVA FRAMEWORK ]
 (LM Studio, Ollama, llama.cpp)     (Runtime + Core + Engine)
            │                                 │
     Lee arquitectura                  Lee arquitectura
     e ignora 'nova.*'                 + Interpreta 'nova.*'
            │                                 │
   Inferencia LLM Normal              Activa MoCE + RAG +
                                      Memoria + Auto-Mejora
```

---

## 3. Generación y Empaquetado

Las nuevas versiones generadas tras sesiones de auto-mejora (`Nova-2B-v2.gguf`, `v3`, etc.)
mantienen estas claves actualizadas con el conteo de habilidades consolidadas.
