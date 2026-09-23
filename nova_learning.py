import sqlite3
import os
import json
from typing import Dict, Any, List, Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "knowledge.db")

class LearningEngine:
    """
    Motor de Aprendizaje y Validación de Candidatos.
    Garantiza proveniencia (fuente, certeza, estado) y permite corregir u olvidar conocimientos.
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
                CREATE TABLE IF NOT EXISTS learning_candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_id TEXT,
                    confidence REAL DEFAULT 0.9,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_learning_status ON learning_candidates(status)
            """)
            conn.commit()

    def register_candidate(
        self,
        topic: str,
        content: str,
        domain: str = "general",
        source_type: str = "user",
        source_id: str = "conversation",
        confidence: float = 0.9,
        status: str = "active",
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Registra un nuevo conocimiento con trazabilidad completa de proveniencia."""
        meta_str = json.dumps(metadata or {}, ensure_ascii=False)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO learning_candidates 
                (topic, content, domain, source_type, source_id, confidence, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (topic.strip(), content.strip(), domain, source_type, source_id, confidence, status, meta_str))
            conn.commit()
            return cursor.lastrowid

    def invalidate(self, candidate_id: int) -> bool:
        """Invalida un conocimiento (olvido / corrección)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE learning_candidates SET status = 'invalidated' WHERE id = ?", (candidate_id,))
            conn.commit()
            return cursor.rowcount > 0

    def list_active(self, domain: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if domain:
                cursor.execute("""
                    SELECT id, topic, content, domain, source_type, confidence, created_at 
                    FROM learning_candidates 
                    WHERE status = 'active' AND domain = ? 
                    ORDER BY id DESC LIMIT ?
                """, (domain, limit))
            else:
                cursor.execute("""
                    SELECT id, topic, content, domain, source_type, confidence, created_at 
                    FROM learning_candidates 
                    WHERE status = 'active' 
                    ORDER BY id DESC LIMIT ?
                """, (limit,))
            return [dict(r) for r in cursor.fetchall()]
