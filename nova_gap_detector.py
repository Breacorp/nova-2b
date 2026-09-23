from typing import Dict, Any, List, Optional
from nova_evaluator import SkillProfileManager

class GapDetector:
    """
    Detector de Brechas de Conocimiento y Habilidad.
    Realiza la autopsia del error y genera un informe de brecha específico.
    """
    def __init__(self, evaluator: SkillProfileManager):
        self.evaluator = evaluator

    def analyze_failure(
        self,
        domain: str,
        skill: str,
        input_prompt: str,
        expected: Any,
        generated: Any
    ) -> Dict[str, Any]:
        """
        Realiza una autopsia estructurada de por qué falló la resolución.
        """
        # Diagnóstico analítico de fallo
        suspected_causes = []
        if domain == "mathematics" or "arithmetic" in skill:
            suspected_causes.append("sequential_state_tracking")
            suspected_causes.append("operator_precedence_or_sign_inversion")
        elif domain == "programming":
            suspected_causes.append("syntax_or_api_deprecation")
            suspected_causes.append("boundary_conditions")
        elif domain == "linguistics":
            suspected_causes.append("false_friends_or_idiomatic_misalignment")
        else:
            suspected_causes.append("semantic_misinterpretation")

        diagnosis = {
            "domain": domain,
            "skill": skill,
            "input": input_prompt,
            "expected": expected,
            "generated": generated,
            "suspected_causes": suspected_causes,
            "severity": "high" if str(expected) != str(generated) else "low"
        }

        # Registrar en el evaluador
        self.evaluator.register_evaluation(
            skill_name=skill,
            domain=domain,
            task=input_prompt,
            expected=str(expected),
            generated=str(generated),
            is_correct=False,
            error_analysis="; ".join(suspected_causes)
        )

        return diagnosis

    def find_active_gaps(self, accuracy_threshold: float = 0.75) -> List[Dict[str, Any]]:
        """Identifica todas las habilidades críticas que requieren intervención."""
        weaknesses = self.evaluator.get_weaknesses(threshold=accuracy_threshold)
        gaps = []
        for w in weaknesses:
            gaps.append({
                "skill": w["skill_name"],
                "domain": w["domain"],
                "accuracy": w["accuracy"],
                "attempts": w["attempts"],
                "gap_severity": "critical" if w["accuracy"] < 0.50 else "moderate"
            })
        return gaps
