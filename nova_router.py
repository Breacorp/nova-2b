import re
from typing import Dict, Any, Optional
from nova_memory import UserMemory
from nova_rag import NovaRAG
from nova_learning import LearningEngine
from nova_experts import CodeExpert, LanguagesExpert, MathExpert

class HybridRouter:
    """
    Enrutador Híbrido de Nova AI.
    Aplica la jerarquía de decisión estricta:
    1. Comandos deterministas del sistema.
    2. Conversación cotidiana y saludos directos (Nova Core).
    3. Consulta de Memoria de Usuario (Personal Facts).
    4. Consulta a Expertos MoCE (Code, Languages, Math).
    5. Consulta al índice RAG (FTS5).
    6. LLM Backend (Último recurso / razonamiento complejo o consultas totalmente nuevas).
    """
    def __init__(
        self,
        memory: UserMemory,
        rag: NovaRAG,
        learning: LearningEngine,
        code_expert: CodeExpert,
        lang_expert: LanguagesExpert,
        math_expert: MathExpert
    ):
        self.memory = memory
        self.rag = rag
        self.learning = learning
        self.code_expert = code_expert
        self.lang_expert = lang_expert
        self.math_expert = math_expert

    def route(self, user_input: str) -> Dict[str, Any]:
        text = user_input.strip()
        lower_text = text.lower()

        # -------------------------------------------------------------
        # NIVEL 1: COMANDOS DEL SISTEMA Y GESTIÓN DE PRIVACIDAD
        # -------------------------------------------------------------
        forget_user_triggers = [
            "/olvidame", "/olvídame", "olvídame", "olvidame",
            "olvida mis datos", "olvidate de mi", "olvídate de mí",
            "borra mis datos", "borra lo que sabes de mi", "borra lo que sabes de mí",
            "borra mi memoria", "elimina mis datos personales", "reinicia mi perfil"
        ]
        if any(lower_text == t or lower_text.startswith(t) for t in forget_user_triggers):
            count = self.memory.clear_all()
            return {
                "layer": "User Memory Privacy",
                "action": "memory_cleared",
                "resolved": True,
                "response": f"He borrado absolutamente todos tus datos personales, preferencias y recuerdos ({count} registros eliminados). Ahora tengo mi perfil de usuario 100% limpio, mientras que todas mis habilidades, razonamiento y conocimientos generales siguen intactos."
            }

        if lower_text in ["/stats", "stats", "/estado"]:
            return {
                "layer": "System Commands",
                "action": "system_stats",
                "resolved": True,
                "response": (
                    f"📊 [Estado del Sistema Nova AI]\n"
                    f"• Memoria Personal de Usuario (user_profile.db): {len(self.memory.get_all())} hechos registrados\n"
                    f"• Documentos en RAG (knowledge.db / FTS5): {self.rag.count_documents()} fragmentos\n"
                    f"• Expertos Activos (MoCE):\n"
                    f"  - CodeExpert: {self.code_expert.count_knowledge()} items\n"
                    f"  - LanguagesExpert: {self.lang_expert.count_knowledge()} items\n"
                    f"  - MathExpert: {self.math_expert.count_knowledge()} items\n"
                    f"• Conocimientos Aprendidos (LearningEngine): {len(self.learning.list_active())} candidatos activos"
                )
            }

        # -------------------------------------------------------------
        # NIVEL 2: APRENDIZAJE EXPLICITO EN CONVERSACIÓN
        # -------------------------------------------------------------
        # Hechos personales: "Mi perro se llama Átomo", "Me llamo José", "Vivo en ..."
        user_fact_match = re.match(r'^(?:mi|me)\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ_]+)\s+(?:se llama|es|son)\s+(.+)', text, re.IGNORECASE)
        if user_fact_match:
            key = user_fact_match.group(1).lower()
            val = user_fact_match.group(2).strip()
            self.memory.set(key, val, category="personal")
            return {
                "layer": "User Memory",
                "action": "memory_stored",
                "resolved": True,
                "response": f"Entendido. Guardé en mi memoria que tu {key} es {val}."
            }

        # Conocimiento general enseñado: "Aprende esto: ...", "Te enseño que: ..."
        learn_match = re.match(r'^(?:te enseño que|aprende esto|guarda esto|aprende que|anota que):\s*(.+)', text, re.IGNORECASE)
        if learn_match:
            fact = learn_match.group(1).strip()
            topic = fact.split(".")[0][:60]
            # Determinar dominio
            domain = "code" if any(k in fact.lower() for k in ["css", "html", "js", "python", "code"]) else "general"
            cid = self.learning.register_candidate(topic=topic, content=fact, domain=domain, source_type="user")
            # Indexar también en RAG
            self.rag.add_document(title=topic, content=fact, source="user_conversation", category=domain)
            return {
                "layer": "Learning Engine",
                "action": "candidate_registered",
                "resolved": True,
                "response": f"✅ Nuevo conocimiento registrado bajo ID #{cid} e indexado en el RAG: '{fact}'"
            }

        # -------------------------------------------------------------
        # NIVEL 3: CONSULTA DE MEMORIA DE USUARIO (DATOS PERSONALES)
        # -------------------------------------------------------------
        # Ejemplo: "¿Cómo se llama mi perro?", "¿Dónde vivo?", "¿Cuál es mi perro?"
        mem_query_match = re.search(r'(?:cómo se llama mi|como se llama mi|cuál es mi|cual es mi|quién es mi|quien es mi)\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ_]+)', text, re.IGNORECASE)
        if mem_query_match:
            key = mem_query_match.group(1).lower().strip("?.! ")
            val = self.memory.get(key)
            if val:
                return {
                    "layer": "User Memory",
                    "action": "memory_retrieved",
                    "resolved": True,
                    "response": f"De acuerdo con mi memoria, tu {key} se llama {val}."
                }

        # Búsqueda general en memoria por coincidencia de términos
        mem_results = self.memory.search(text)
        if mem_results:
            first = mem_results[0]
            if first["key"] in lower_text:
                return {
                    "layer": "User Memory",
                    "action": "memory_retrieved",
                    "resolved": True,
                    "response": f"De acuerdo con mi memoria: Tu {first['key']} es {first['value']}."
                }


        # -------------------------------------------------------------
        # NIVEL 5: CONSULTA A EXPERTOS MoCE
        # -------------------------------------------------------------
        expert_candidates = []
        code_words = ["css", "html", "javascript", "js", "python", "código", "flexbox", "grid", "función", "api", "async"]
        lang_words = ["chino", "mandarín", "inglés", "francés", "portugués", "español", "idioma", "traducción", "gramática"]
        math_words = ["álgebra", "algebra", "matemática", "matematica", "ecuación", "fórmula", "integral", "derivada", "matriz"]

        if any(w in lower_text for w in code_words):
            expert_candidates.append(self.code_expert)
        if any(w in lower_text for w in lang_words):
            expert_candidates.append(self.lang_expert)
        if any(w in lower_text for w in math_words):
            expert_candidates.append(self.math_expert)

        for expert in expert_candidates:
            matches = expert.search(text, limit=2)
            if matches:
                top = matches[0]
                return {
                    "layer": f"MoCE ({expert.name})",
                    "action": "expert_direct_resolution",
                    "resolved": True,
                    "response": f"💡 [{expert.name} — {top['topic']}]:\n\n{top['content']}"
                }

        # -------------------------------------------------------------
        # NIVEL 6: CONSULTA AL RAG ULTRALIGERO (FTS5)
        # -------------------------------------------------------------
        rag_hits = self.rag.search(text, limit=2)
        if rag_hits:
            best_hit = rag_hits[0]
            tokens = [t for t in lower_text.split() if len(t) > 3]
            hit_text = (best_hit['title'] + " " + best_hit['content']).lower()
            matching_tokens = [t for t in tokens if t in hit_text]
            if len(matching_tokens) >= 2 or (len(tokens) == 1 and len(matching_tokens) == 1):
                clean_rag_content = best_hit['content']
                if "Respuesta:" in clean_rag_content:
                    clean_rag_content = clean_rag_content.split("Respuesta:", 1)[1].strip()
                return {
                    "layer": "Nova RAG (FTS5)",
                    "action": "rag_grounded_response",
                    "resolved": True,
                    "response": clean_rag_content
                }

        # -------------------------------------------------------------
        # NIVEL 6: DELEGACIÓN DIRECTA AL MOTOR LLM (Inferencia Nativa de Nova 2B)
        # -------------------------------------------------------------
        llm_response = self._invoke_llm(user_input)
        if llm_response:
            return {
                "layer": "Nova 2B (Native LLM Engine)",
                "action": "native_llm_generation",
                "resolved": True,
                "response": llm_response
            }

        # En caso de fallo excepcional en la comunicación con el motor de inferencia:
        return {
            "layer": "Nova Engine",
            "action": "direct_answer",
            "resolved": True,
            "response": "Acá estoy, che. Tuve un micro-parpadeo de conexión con mi motor de inferencia, ¿me repetís?"
        }

    def _invoke_llm(self, prompt: str) -> Optional[str]:
        """
        Invoca el backend LLM de Nova 2B con soporte de búsqueda en tiempo real si la pregunta es factual.
        """
        import re
        import json
        import urllib.request

        # Si el usuario pregunta por hechos actuales, productos recientes o pide buscar información:
        grounded_context = None
        factual_keywords = ["nuevo", "nueva", "ultimo", "último", "lanzamiento", "precio", "colores", "iphone", "apple", "noticias", "busca", "informacion real", "información real"]
        if any(k in prompt.lower() for k in factual_keywords):
            try:
                from nova_web_search import NovaWebSearch
                if not hasattr(self, "_web_search"):
                    self._web_search = NovaWebSearch()
                grounded_context = self._web_search.get_grounded_context(prompt)
            except Exception:
                pass

        # 1. Intentar con el Motor Nativo Propietario de Nova AI
        try:
            from nova_engine import NovaEngineManager
            if not hasattr(self, "_native_engine"):
                self._native_engine = NovaEngineManager(port=18888)
            native_reply = self._native_engine.generate(prompt, grounded_context=grounded_context)
            if native_reply:
                cleaned = re.sub(r'<commentary>.*?</commentary>', '', native_reply, flags=re.DOTALL)
                cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL)
                cleaned = re.sub(r'<thought>.*?</thought>', '', cleaned, flags=re.DOTALL).strip()
                if cleaned:
                    return cleaned
        except Exception:
            pass

        # 2. Fallback secundario a Ollama si existe
        model_candidates = ["modernotech/Nova-2b:latest", "hf.co/modernotech/Nova-2b:latest"]
        for model_name in model_candidates:
            try:
                req_data = json.dumps({
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_ctx": 4096
                    }
                }).encode("utf-8")

                req = urllib.request.Request(
                    "http://127.0.0.1:11434/api/generate",
                    data=req_data,
                    headers={"Content-Type": "application/json"}
                )

                with urllib.request.urlopen(req, timeout=12) as response:
                    if response.status == 200:
                        res_json = json.loads(response.read().decode("utf-8"))
                        raw_text = res_json.get("response", "").strip()

                        cleaned = re.sub(r'<commentary>.*?</commentary>', '', raw_text, flags=re.DOTALL)
                        cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL)
                        cleaned = re.sub(r'<thought>.*?</thought>', '', cleaned, flags=re.DOTALL).strip()

                        if cleaned:
                            return cleaned
            except Exception:
                continue

        return None
