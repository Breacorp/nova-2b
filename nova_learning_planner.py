import sqlite3
import os
from typing import Dict, Any, List, Optional
from nova_evaluator import SkillProfileManager
from nova_gap_detector import GapDetector
from nova_curiosity import CuriosityEngine
from nova_curriculum import CurriculumGenerator

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "knowledge.db")

class LearningPlanner:
    """
    Planificador de Aprendizaje Autónomo de Nova AI.
    Conecta las brechas detectadas por GapDetector con el CurriculumGenerator y los recursos de RAG.
    """
    def __init__(
        self,
        evaluator: SkillProfileManager,
        gap_detector: GapDetector,
        curiosity: CuriosityEngine,
        curriculum: CurriculumGenerator,
        db_path: str = DEFAULT_DB_PATH
    ):
        self.evaluator = evaluator
        self.gap_detector = gap_detector
        self.curiosity = curiosity
        self.curriculum = curriculum
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    priority REAL DEFAULT 1.0,
                    status TEXT DEFAULT 'pending',
                    target_accuracy REAL DEFAULT 0.90,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            conn.commit()

    def create_goal(self, skill_name: str, domain: str, priority: float = 1.0) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO learning_goals (skill_name, domain, priority, status)
                VALUES (?, ?, ?, 'active')
            """, (skill_name, domain, priority))
            conn.commit()
            return cursor.lastrowid

    def generate_next_session(self) -> Optional[Dict[str, Any]]:
        """
        Calcula y retorna la próxima sesión de autoaprendizaje según prioridad.
        """
        # 1. Obtener brechas activas
        gaps = self.gap_detector.find_active_gaps()
        if gaps:
            top_gap = gaps[0]
            drills = self.curriculum.generate_practice_batch(top_gap["skill"], count=5)
            return {
                "source": "gap_driven",
                "skill": top_gap["skill"],
                "domain": top_gap["domain"],
                "drills": drills,
                "goal": f"Superar debilidad en {top_gap['skill']} (Precisión actual: {top_gap['accuracy'] * 100}%)"
            }

        # 2. Si no hay brechas urgentes, aprendizaje guiado por Curiosidad
        priority_domain = self.curiosity.get_priority_domain([])
        skill_name = f"{priority_domain}_advanced_patterns"
        drills = self.curriculum.generate_practice_batch(skill_name, count=5)
        return {
            "source": "curiosity_driven",
            "skill": skill_name,
            "domain": priority_domain,
            "drills": drills,
            "goal": f"Exploración autónoma orientada a curiosidad en {priority_domain}"
        }
