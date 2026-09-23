#!/usr/bin/env python3
"""
Nova Core — Orquestador Central de Nova AI
Desarrollado por ModernoTech.

Orquesta la arquitectura modular completa:
- Router Híbrido (HybridRouter)
- Memoria de Usuario (UserMemory)
- RAG Ultraligero SQLite FTS5 (NovaRAG)
- Motor de Aprendizaje y Validación (LearningEngine)
- Mixture of Code-Experts (CodeExpert, LanguagesExpert, MathExpert)
- Motor de Asimilación de Archivos (NovaAssimilator)
"""

import os
import sys
from typing import Dict, Any, List, Optional

from nova_memory import UserMemory
from nova_rag import NovaRAG
from nova_learning import LearningEngine
from nova_router import HybridRouter
from nova_assimilator import NovaAssimilator
from nova_experts import CodeExpert, LanguagesExpert, MathExpert

# Componentes del Self-Improvement Engine
from nova_evaluator import SkillProfileManager
from nova_gap_detector import GapDetector
from nova_curiosity import CuriosityEngine
from nova_curriculum import CurriculumGenerator
from nova_verifier import VerificationEngine
from nova_learning_planner import LearningPlanner
from nova_self_improve import SelfImprovementEngine

class NovaCore:
    def __init__(self, db_path: str = None):
        self.memory = UserMemory(db_path=db_path) if db_path else UserMemory()
        self.rag = NovaRAG(db_path=db_path) if db_path else NovaRAG()
        self.learning = LearningEngine(db_path=db_path) if db_path else LearningEngine()
        
        self.code_expert = CodeExpert(db_path=db_path) if db_path else CodeExpert()
        self.languages_expert = LanguagesExpert(db_path=db_path) if db_path else LanguagesExpert()
        self.math_expert = MathExpert(db_path=db_path) if db_path else MathExpert()

        # Inicialización del subsistema de auto-mejora
        self.evaluator = SkillProfileManager(db_path=db_path) if db_path else SkillProfileManager()
        self.gap_detector = GapDetector(evaluator=self.evaluator)
        self.curiosity = CuriosityEngine(db_path=db_path) if db_path else CuriosityEngine()
        self.curriculum = CurriculumGenerator()
        self.verifier = VerificationEngine()
        self.planner = LearningPlanner(
            evaluator=self.evaluator,
            gap_detector=self.gap_detector,
            curiosity=self.curiosity,
            curriculum=self.curriculum,
            db_path=db_path or self.evaluator.db_path
        )
        self.self_improve = SelfImprovementEngine(
            evaluator=self.evaluator,
            gap_detector=self.gap_detector,
            curiosity=self.curiosity,
            curriculum=self.curriculum,
            verifier=self.verifier,
            planner=self.planner,
            learning_engine=self.learning,
            rag=self.rag
        )

        self.assimilator = NovaAssimilator(
            code_expert=self.code_expert,
            lang_expert=self.languages_expert,
            math_expert=self.math_expert,
            rag=self.rag
        )

        self.router = HybridRouter(
            memory=self.memory,
            rag=self.rag,
            learning=self.learning,
            code_expert=self.code_expert,
            lang_expert=self.languages_expert,
            math_expert=self.math_expert
        )


    def ask(self, user_prompt: str) -> Dict[str, Any]:
        """Procesa una consulta a través del Router Híbrido jerárquico."""
        return self.router.route(user_prompt)

    def ingest(self, file_path: str, domain_hint: str = None) -> List[Dict[str, Any]]:
        """Ingiere un manual, documento o archivo de código en el sistema."""
        return self.assimilator.ingest_file(file_path, domain_hint)

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas completas de todas las capas de inteligencia."""
        return {
            "UserMemory": len(self.memory.get_all()),
            "RAGDocuments": self.rag.count_documents(),
            "LearningCandidates": len(self.learning.list_active()),
            "MoCE": {
                "CodeExpert": self.code_expert.count_knowledge(),
                "LanguagesExpert": self.languages_expert.count_knowledge(),
                "MathExpert": self.math_expert.count_knowledge()
            }
        }

def run_cli():
    print("=" * 70)
    print("  🚀 NOVA AI — Arquitectura Híbrida Completa | ModernoTech")
    print("  Core + Memory + MoCE + RAG (FTS5) + Learning Engine")
    print("=" * 70)
    core = NovaCore()
    stats = core.get_stats()
    print(f"📊 Estado Inicial:")
    print(f"   • Hechos en Memoria: {stats['UserMemory']}")
    print(f"   • Documentos RAG: {stats['RAGDocuments']}")
    print(f"   • Expertos MoCE: {stats['MoCE']['CodeExpert'] + stats['MoCE']['LanguagesExpert'] + stats['MoCE']['MathExpert']} items")
    print("\n💡 Instrucciones de prueba:")
    print("   - Charla cotidiana: 'Hola', '¿Quién te creó?' (Nova Core)")
    print("   - Memoria: 'Mi perro se llama Átomo' -> '¿Cómo se llama mi perro?'")
    print("   - MoCE: 'Cómo centrar en CSS', 'Regla de la cadena', 'Infinitivo en portugués'")
    print("   - Aprender: 'Aprende esto: <hecho nuevo>'")
    print("   - Estado: '/stats'")
    print("   - Salir: 'exit' o 'salir'\n" + "-" * 70)

    while True:
        try:
            prompt = input("\nUsuario > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ["exit", "salir", "quit"]:
                print("Sesión finalizada. El conocimiento persiste en storage/knowledge.db.")
                break

            if prompt.lower() in ["/improve", "improve", "/auto-mejora"]:
                print("\n⚙️ [Self-Improvement Engine]: Ejecutando ciclo autónomo...")
                result = core.self_improve.run_self_improvement_cycle()
                print(f"🎯 Habilidad atacada: {result['target_skill']} ({result['domain']})")
                print(f"📊 Desempeño: {result['accuracy'] * 100}% | Resultado: {result['outcome']}")
                print(f"📦 Estado de Consolidación: {result['consolidation']}")
                continue

            if prompt.lower() in ["/skills", "skills", "/habilidades"]:
                skills = core.evaluator.get_all_skills()
                print("\n📊 [Skill Profile — Rendimiento Interno]:")
                if not skills:
                    print("   Sin evaluaciones registradas aún. Corre '/improve' para iniciar una sesión.")
                for s in skills:
                    print(f"   • {s['skill_name']} ({s['domain']}): {round(s['accuracy']*100, 1)}% ({s['correct']}/{s['attempts']})")
                continue

            result = core.ask(prompt)
            print(f"\n[{result['layer']}]:")
            print(result["response"])


        except (KeyboardInterrupt, EOFError):
            print("\nCerrando Nova AI...")
            break

if __name__ == "__main__":
    run_cli()
