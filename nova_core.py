#!/usr/bin/env python3
"""
Nova Core — Orquestador Mixture of Code-Experts (MoCE)
Desarrollado por ModernoTech.

Combina:
1. Nova Core (Router de intención y búsqueda de conocimientos aprendidos).
2. Expertos vivos en Python (Code, Languages, Math).
3. Motor de Asimilación (Ingesta de documentos y aprendizaje continuo sin tocar pesos).
4. Gateway LLM local hacia Nova 2B (GGUF via llama.cpp / API).
"""

import os
import sys
import re
from typing import Dict, Any, List, Optional
from nova_experts import CodeExpert, LanguagesExpert, MathExpert
from nova_assimilator import NovaAssimilator

class NovaCore:
    def __init__(self, db_path: str = None):
        self.code_expert = CodeExpert(db_path=db_path)
        self.languages_expert = LanguagesExpert(db_path=db_path)
        self.math_expert = MathExpert(db_path=db_path)
        self.assimilator = NovaAssimilator(
            code_expert=self.code_expert,
            lang_expert=self.languages_expert,
            math_expert=self.math_expert
        )

    def route_query(self, query: str) -> List[Any]:
        """Detecta los expertos relevantes para la consulta del usuario."""
        q_lower = query.lower()
        active_experts = []

        code_triggers = ["css", "html", "javascript", "js", "python", "código", "codigo", "programar", "función", "funcion", "script", "flexbox", "grid"]
        lang_triggers = ["chino", "mandarín", "mandarin", "inglés", "ingles", "francés", "frances", "portugués", "portugues", "español", "traducir", "idioma", "gramática"]
        math_triggers = ["matemática", "matematica", "álgebra", "algebra", "ecuación", "ecuacion", "integral", "derivada", "matriz", "calcular", "fórmula", "formula"]

        if any(w in q_lower for w in code_triggers):
            active_experts.append(self.code_expert)
        if any(w in q_lower for w in lang_triggers):
            active_experts.append(self.languages_expert)
        if any(w in q_lower for w in math_triggers):
            active_experts.append(self.math_expert)

        # Si no hubo match específico, consultar a todos los expertos por búsqueda de texto
        if not active_experts:
            active_experts = [self.code_expert, self.languages_expert, self.math_expert]

        return active_experts

    def ask(self, user_prompt: str) -> Dict[str, Any]:
        """
        Procesa una consulta del usuario:
        1. Comprueba si es una orden de enseñanza explícita ('te enseño que...', 'aprende esto:').
        2. Si no, busca en la base de datos de los expertos relevantes.
        3. Si encuentra respuesta exacta, responde directamente (Core Resolution).
        4. Si requiere síntesis, genera el prompt enriquecido para Nova 2B (LLM Engine).
        """
        # 1. Detección de comando de aprendizaje conversacional directo
        learn_match = re.match(r'^(?:te enseño que|aprende esto|guarda esto|aprende que|anota que):\s*(.+)', user_prompt, re.IGNORECASE)
        if learn_match:
            fact = learn_match.group(1).strip()
            topic = fact.split(".")[0][:60]
            result = self.assimilator.assimilate_entry(topic=topic, content=fact)
            return {
                "source": "Nova Core (Aprendizaje Instantáneo)",
                "action": "learned",
                "expert": result["expert"],
                "response": f"✅ He aprendido y guardado este conocimiento en el experto [{result['expert']}]: '{fact}'"
            }

        # 2. Búsqueda en los expertos
        experts = self.route_query(user_prompt)
        collected_knowledge = []

        for exp in experts:
            results = exp.search(user_prompt, limit=3)
            for r in results:
                collected_knowledge.append({
                    "expert": exp.name,
                    "topic": r["topic"],
                    "content": r["content"]
                })

        if collected_knowledge:
            # Respuesta rápida de Nova Core con conocimiento verificado
            best_match = collected_knowledge[0]
            context_summary = "\n---\n".join([f"[{k['expert']} / {k['topic']}]:\n{k['content']}" for k in collected_knowledge[:2]])
            return {
                "source": f"Nova Core ({best_match['expert']})",
                "action": "expert_knowledge_retrieved",
                "knowledge_used": collected_knowledge,
                "response": f"💡 [Conocimiento Verificado de {best_match['expert']}]:\n\n{context_summary}"
            }

        # 3. Fallback: Requiere intervención del LLM como profesor
        return {
            "source": "Nova 2B (LLM Engine)",
            "action": "requires_llm",
            "knowledge_used": [],
            "response": f"🤖 Esta consulta aún no está indexada en el núcleo de expertos. Se delega a Nova 2B LLM para procesar, responder y asimilar."
        }

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de conocimiento adquirido por cada experto."""
        return {
            "CodeExpert": self.code_expert.count_knowledge(),
            "LanguagesExpert": self.languages_expert.count_knowledge(),
            "MathExpert": self.math_expert.count_knowledge(),
            "TotalKnowledgeItems": (
                self.code_expert.count_knowledge() +
                self.languages_expert.count_knowledge() +
                self.math_expert.count_knowledge()
            )
        }

def run_cli():
    print("=" * 65)
    print("  🚀 NOVA AI — Mixture of Code-Experts (MoCE) | ModernoTech")
    print("=" * 65)
    core = NovaCore()
    stats = core.get_stats()
    print(f"📊 Estado del Núcleo: {stats['TotalKnowledgeItems']} conocimientos activos")
    print(f"   • CodeExpert: {stats['CodeExpert']} items (Python, JS, HTML5, CSS3)")
    print(f"   • LanguagesExpert: {stats['LanguagesExpert']} items (ZH, EN, FR, PT, ES)")
    print(f"   • MathExpert: {stats['MathExpert']} items (Álgebra, Cálculo, Lógica)")
    print("\n💡 Comandos disponibles:")
    print("   - Escribe cualquier pregunta técnica.")
    print("   - Para enseñar: 'Aprende esto: <tu conocimiento>'")
    print("   - Para salir: 'exit' o 'salir'\n" + "-" * 65)

    while True:
        try:
            prompt = input("\nUsuario > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ["exit", "salir", "quit"]:
                print("Hasta luego. Nova Core se mantiene en memoria.")
                break

            result = core.ask(prompt)
            print(f"\n[{result['source']}]:")
            print(result["response"])

        except (KeyboardInterrupt, EOFError):
            print("\nCerrando sesión de Nova AI...")
            break

if __name__ == "__main__":
    run_cli()
