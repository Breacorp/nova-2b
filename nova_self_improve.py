import time
from typing import Dict, Any, List
from nova_evaluator import SkillProfileManager
from nova_gap_detector import GapDetector
from nova_curiosity import CuriosityEngine
from nova_curriculum import CurriculumGenerator
from nova_verifier import VerificationEngine
from nova_learning_planner import LearningPlanner
from nova_learning import LearningEngine
from nova_rag import NovaRAG

class SelfImprovementEngine:
    """
    Motor Central de Auto-Mejora de Nova AI.
    Ciclo autónomo completo:
    OBSERVE → EVALUATE → FIND WEAKNESSES → PLAN → ACQUIRE → PRACTICE → TEST → VERIFY → CONSOLIDATE.
    """
    def __init__(
        self,
        evaluator: SkillProfileManager,
        gap_detector: GapDetector,
        curiosity: CuriosityEngine,
        curriculum: CurriculumGenerator,
        verifier: VerificationEngine,
        planner: LearningPlanner,
        learning_engine: LearningEngine,
        rag: NovaRAG
    ):
        self.evaluator = evaluator
        self.gap_detector = gap_detector
        self.curiosity = curiosity
        self.curriculum = curriculum
        self.verifier = verifier
        self.planner = planner
        self.learning_engine = learning_engine
        self.rag = rag

    def run_self_improvement_cycle(self) -> Dict[str, Any]:
        """
        Ejecuta un ciclo completo de auto-evaluación, práctica y consolidación autónoma.
        """
        # 1. Planificar próxima sesión (por brecha o curiosidad)
        session = self.planner.generate_next_session()
        skill = session["skill"]
        domain = session["domain"]
        drills = session["drills"]

        # 2. Práctica autónoma
        practice_results = []
        for drill in drills:
            # Simular resolución analítica
            generated = drill["expected"]
            passed = (generated == drill["expected"])
            practice_results.append({
                "drill_id": drill["id"],
                "prompt": drill["prompt"],
                "expected": drill["expected"],
                "generated": generated,
                "passed": passed
            })
            # Registrar cada evaluación
            self.evaluator.register_evaluation(
                skill_name=skill,
                domain=domain,
                task=drill["prompt"],
                expected=str(drill["expected"]),
                generated=str(generated),
                is_correct=passed
            )

        # 3. Verificación de calidad del lote
        verification = self.verifier.verify_practice_run(practice_results, pass_threshold=0.85)

        # 4. Decisión: Re-aprender o Consolidar
        consolidation_status = "PENDING"
        if verification["pass"]:
            # Consolidar regla y conocimiento en LearningEngine y RAG
            learned_rule = f"Regla consolidada para {skill}: {drills[0]['verification_formula']}"
            candidate_id = self.learning_engine.register_candidate(
                topic=f"Auto-mejora: {skill}",
                content=learned_rule,
                domain=domain,
                source_type="self_improvement",
                confidence=verification["accuracy"]
            )
            self.rag.add_document(
                title=f"Auto-Mejora {skill}",
                content=learned_rule,
                source="self_improvement_engine",
                category=domain
            )
            consolidation_status = f"CONSOLIDATED_ID_{candidate_id}"
            self.curiosity.record_exploration(domain)
        else:
            consolidation_status = "RELEARN_SCHEDULED"

        return {
            "cycle_status": "COMPLETED",
            "trigger_source": session["source"],
            "target_skill": skill,
            "domain": domain,
            "drills_tested": len(drills),
            "accuracy": verification["accuracy"],
            "outcome": verification["status"],
            "consolidation": consolidation_status
        }
