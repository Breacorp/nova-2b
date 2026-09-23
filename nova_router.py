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
        # NIVEL 1: COMANDOS DEL SISTEMA
        # -------------------------------------------------------------
        if lower_text in ["/stats", "stats", "/estado"]:
            return {
                "layer": "System Commands",
                "action": "system_stats",
                "resolved": True,
                "response": (
                    f"📊 [Estado del Sistema Nova AI]\n"
                    f"• Memoria de Usuario: {len(self.memory.get_all())} hechos registrados\n"
                    f"• Documentos en RAG (FTS5): {self.rag.count_documents()} fragmentos\n"
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
        # NIVEL 3: CONVERSACION COTIDIANA DETERMINISTA (NOVA CORE)
        # -------------------------------------------------------------
        greetings = {
            "hola": "¡Hola! ¿Cómo estás? Soy Nova AI, lista para ayudarte.",
            "buenos días": "¡Buenos días! ¿En qué podemos avanzar hoy?",
            "buenas tardes": "¡Buenas tardes! ¿Qué proyecto o consulta técnica tienes?",
            "buenas noches": "¡Buenas noches! ¿En qué te puedo colaborar?",
            "cómo estás": "Excelente, con todos mis módulos y expertos listos para operar.",
            "quién eres": "Soy Nova 2B (Nova AI), una inteligencia artificial híbrida ultracompacta desarrollada por ModernoTech.",
            "quien te creo": "Fui concebida y desarrollada por ModernoTech / José Luis Brea.",
            "quién te creó": "Fui concebida y desarrollada por ModernoTech / José Luis Brea."
        }
        for g_trigger, g_reply in greetings.items():
            if lower_text == g_trigger or lower_text == f"{g_trigger}!" or lower_text == f"{g_trigger}.":
                return {
                    "layer": "Nova Core (Determinista)",
                    "action": "greeting",
                    "resolved": True,
                    "response": g_reply
                }

        # -------------------------------------------------------------
        # NIVEL 4: CONSULTA DE MEMORIA DE USUARIO
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
            # Si el documento tiene información relevante directa
            return {
                "layer": "Nova RAG (FTS5)",
                "action": "rag_grounded_response",
                "resolved": True,
                "response": (
                    f"📄 [RAG FTS5 / Fuente: {best_hit['source']} | {best_hit['title']}]:\n\n"
                    f"{best_hit['content']}"
                )
            }

        # -------------------------------------------------------------
        # NIVEL 7: DELEGACION AL LLM ENGINE (Razonamiento / Fallback)
        # -------------------------------------------------------------
        return {
            "layer": "Nova 2B (LLM Backend)",
            "action": "forward_to_llm",
            "resolved": False,
            "response": (
                "🤖 Consulta no resuelta en capas locales directas (Core, Memory, MoCE, RAG). "
                "Requiere derivación al LLM Nova 2B como motor de razonamiento y profesor."
            )
        }
