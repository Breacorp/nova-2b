import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "knowledge.db")

class UserMemory:
    """
    Gestiona la memoria persistente del usuario (hechos personales, preferencias y contexto).
    Permite responder preguntas directas sin necesidad de invocar al LLM.
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
                CREATE TABLE IF NOT EXISTS user_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    confidence REAL DEFAULT 1.0,
                    source TEXT DEFAULT 'user',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_key ON user_memory(key)
            """)
            conn.commit()

    def set(self, key: str, value: str, category: str = "general", source: str = "user") -> None:
        """Guarda o actualiza un hecho en la memoria del usuario."""
        clean_key = key.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_memory (key, value, category, source, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    category = excluded.category,
                    source = excluded.source,
                    updated_at = CURRENT_TIMESTAMP
            """, (clean_key, value.strip(), category, source))
            conn.commit()

    def get(self, key: str) -> Optional[str]:
        """Obtiene un hecho por su clave exacta."""
        clean_key = key.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_memory WHERE key = ?", (clean_key,))
            row = cursor.fetchone()
            return row[0] if row else None

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Busca en la memoria hechos coincidentes por clave o valor."""
        tokens = query.lower().split()
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            conditions = []
            params = []
            for t in tokens:
                if len(t) > 2:
                    conditions.append("(LOWER(key) LIKE ? OR LOWER(value) LIKE ?)")
                    params.extend([f"%{t}%", f"%{t}%"])
            if not conditions:
                return []
            sql = f"SELECT key, value, category, updated_at FROM user_memory WHERE {' OR '.join(conditions)} LIMIT 5"
            cursor.execute(sql, params)
            return [dict(r) for r in cursor.fetchall()]

    def delete(self, key: str) -> bool:
        """Elimina un hecho de la memoria."""
        clean_key = key.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_memory WHERE key = ?", (clean_key,))
            conn.commit()
            return cursor.rowcount > 0

    def get_all(self) -> Dict[str, str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM user_memory")
            return {r[0]: r[1] for r in cursor.fetchall()}
