import sqlite3
import os
import json
from typing import Dict, Any, List, Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "knowledge.db")

class SkillProfileManager:
    """
    Rastrea métricas internas de desempeño por habilidad (Skill Profile).
    Permite calcular accuracy, detectar tendencias de declive y alimentar al Gap Detector.
    """
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT UNIQUE NOT NULL,
                    domain TEXT NOT NULL,
                    attempts INTEGER DEFAULT 0,
                    correct INTEGER DEFAULT 0,
                    accuracy REAL DEFAULT 0.0,
                    recent_accuracy REAL DEFAULT 0.0,
                    trend TEXT DEFAULT 'stable',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL,
                    task_prompt TEXT NOT NULL,
                    expected_output TEXT NOT NULL,
                    generated_output TEXT NOT NULL,
                    is_correct INTEGER NOT NULL,
                    error_analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def register_evaluation(self, skill_name: str, domain: str, task: str, expected: str, generated: str, is_correct: bool, error_analysis: Optional[str] = None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evaluation_results (skill_name, task_prompt, expected_output, generated_output, is_correct, error_analysis)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (skill_name, task, str(expected), str(generated), 1 if is_correct else 0, error_analysis or ""))

            # Actualizar o insertar métricas en tabla skills
            cursor.execute("SELECT attempts, correct FROM skills WHERE skill_name = ?", (skill_name,))
            row = cursor.fetchone()
            if row:
                att, corr = row[0] + 1, row[1] + (1 if is_correct else 0)
                acc = round(corr / att, 4)
                cursor.execute("""
                    UPDATE skills SET attempts = ?, correct = ?, accuracy = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE skill_name = ?
                """, (att, corr, acc, skill_name))
            else:
                corr = 1 if is_correct else 0
                cursor.execute("""
                    INSERT INTO skills (skill_name, domain, attempts, correct, accuracy, recent_accuracy, trend)
                    VALUES (?, ?, 1, ?, ?, ?, 'stable')
                """, (skill_name, domain, corr, float(corr), float(corr)))
            conn.commit()

    def get_skill(self, skill_name: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skills WHERE skill_name = ?", (skill_name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_skills(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skills ORDER BY accuracy ASC")
            return [dict(r) for r in cursor.fetchall()]

    def get_weaknesses(self, threshold: float = 0.75) -> List[Dict[str, Any]]:
        """Devuelve habilidades con precisión inferior al umbral especificado."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skills WHERE accuracy < ? ORDER BY accuracy ASC", (threshold,))
            return [dict(r) for r in cursor.fetchall()]
