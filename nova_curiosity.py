import sqlite3
import os
from typing import Dict, Any, List

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "knowledge.db")

class CuriosityEngine:
    """
    Motor de Curiosidad y Exploración Autónoma de Nova AI.
    Calcula el interés de exploración según:
    frecuencia de consulta, volumen de errores, novedad y conexiones entre conceptos.
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
                CREATE TABLE IF NOT EXISTS curiosity_profiles (
                    domain TEXT PRIMARY KEY,
                    interest REAL DEFAULT 0.5,
                    exploration_count INTEGER DEFAULT 0,
                    last_explored TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Valores semilla auditables
            initial_domains = [
                ("programming", 0.92),
                ("mathematics", 0.85),
                ("linguistics", 0.70),
                ("logic", 0.88),
                ("systems_architecture", 0.90)
            ]
            for dom, score in initial_domains:
                cursor.execute("""
                    INSERT OR IGNORE INTO curiosity_profiles (domain, interest) VALUES (?, ?)
                """, (dom, score))
            conn.commit()

    def get_priority_domain(self, weakness_domains: List[str]) -> str:
        """
        Determina qué dominio explorar o reforzar combinando debilidad + curiosidad.
        """
        if weakness_domains:
            return weakness_domains[0]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT domain FROM curiosity_profiles ORDER BY interest DESC LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else "programming"

    def record_exploration(self, domain: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE curiosity_profiles 
                SET exploration_count = exploration_count + 1, last_explored = CURRENT_TIMESTAMP
                WHERE domain = ?
            """, (domain,))
            conn.commit()

    def get_all_scores(self) -> Dict[str, float]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT domain, interest FROM curiosity_profiles ORDER BY interest DESC")
            return {r[0]: r[1] for r in cursor.fetchall()}
