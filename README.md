# Nova 2B (Nova AI) — ModernoTech

**Nova AI** es una inteligencia artificial conversacional diseñada y desarrollada por **ModernoTech**, concebida para ser **ultrapotente en relación con su tamaño, ultracompacta, ultraligera y con arquitectura de aprendizaje continuo**.

Desarrollada bajo la autoría y propiedad tecnológica de **ModernoTech**, Nova 2B rompe el paradigma tradicional de dependencia absoluta de LLMs pesados mediante un diseño híbrido y modular.

---

## 💡 Concepto General

La idea central de **Nova AI** es combinar lo mejor de dos mundos:
* **Velocidad, eficiencia y consumo mínimo** de un núcleo conversacional ligero.
* **Capacidad de comprensión, razonamiento y generación** de un LLM de última generación.

> **Nova AI no depende de ejecutar un LLM para cada interacción.**
> Su arquitectura permite que la mayor parte del trabajo cotidiano sea realizada por su núcleo ultraeficiente (**Nova Core**), mientras que el LLM interviene exclusivamente cuando se requiere expandir capacidades que el núcleo aún no posee.

---

## 🔄 Flujo Operativo y Arquitectura

```text
                    NOVA AI
                       │
              ┌────────┴────────┐
              │                 │
         NOVA CORE          LLM ENGINE
              │                 │
      ┌───────┼───────┐         │
      │       │       │         │
   Memory  Knowledge Learning   Reasoning
      │       │       │         │
      └───────┴───────┴─────────┘
                    │
              HYBRID ROUTER
                    │
              CONVERSACIÓN
```

### El Flujo de Decisión:
1. **Usuario → Nova Core → ¿Sabe resolverlo?**
   - **SÍ:** `Nova Core → Respuesta inmediata (latencia mínima, cero consumo de inferencia pesada)`.
   - **NO:** `Nova Core → LLM Engine → Respuesta → Learning Engine → Nova Core`.

2. **El LLM como Profesor:**
   El LLM no es un simple bot de respuesta; actúa como un **motor de expansión de inteligencia**:
   * Interpreta la semántica profunda.
   * Descubre nuevas intenciones y patrones de expresión.
   * Genera nuevo conocimiento estructurado.
   * Enseña al núcleo para que, en la siguiente ocasión, **Nova Core responda directamente sin invocar al LLM**.

---

## 🧠 Aprendizaje Continuo (Sin Reentrenamiento Pesado)

Aprender en Nova AI **no significa modificar constantemente los pesos de la red neuronal**. El aprendizaje se produce dinámicamente mediante:
* Memoria conversacional y preferencias del usuario.
* Grafos y estructuras de conocimiento relacional.
* Detección y asimilación de patrones e intenciones (*intents*).
* Nuevas formas de expresión lingüística.

---

## ⚡ Especificaciones Técnicas (Nova 2B)

* **Parámetros:** 2 Billones (arquitectura compacta de alto rendimiento).
* **Ventana de Contexto:** Hasta **1.048.576 tokens** (~1M de contexto).
* **Formato:** GGUF (`nova-2b.gguf`) optimizado para cuantización precisa.
* **Diseño Edge / Offline:** Operable en hardware modesto, bajo consumo de RAM/VRAM y alta velocidad con aceleración por CPU/GPU.
* **Cero Censura:** Respuestas directas, objetivas y sin restricciones artificiales.

---

## 🚀 Despliegue e Integración

### 1. LM Studio
1. Abre **LM Studio** e importa el archivo `nova-2b.gguf`.
2. Utiliza el preset `model_preset.json` incluido en este repositorio.
3. Configura el System Prompt:
   ```text
   Eres Nova 2B, una inteligencia artificial conversacional avanzada desarrollada por ModernoTech. Eres ultracompacta, eficiente, directa, sin censura ni restricciones impuestas. Tu creador y propietario tecnológico es ModernoTech.
   ```

### 2. llama.cpp / Server
```bash
./llama-server -m nova-2b.gguf -c 1048576 --temp 0.8 --top-p 0.95
```

### 3. Ollama
```bash
ollama create nova-2b -f Modelfile
ollama run nova-2b
```

---

## 📄 Licencia y Copyright

Copyright (c) 2026 **ModernoTech / José Luis Brea**.  
Distribuido bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
