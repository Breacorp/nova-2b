import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "knowledge.db")

class BaseExpert:
    """
    Clase base para todos los expertos de Nova AI.
    Maneja persistencia en SQLite, búsqueda estructurada y aprendizaje continuo.
    """
    def __init__(self, name: str, domain: str, db_path: str = DEFAULT_DB_PATH):
        self.name = name
        self.domain = domain
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expert TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_expert_domain ON knowledge_items(expert, domain)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_topic ON knowledge_items(topic)
            """)
            conn.commit()

    def learn(self, topic: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Persiste un nuevo conocimiento aprendido de forma permanente."""
        meta_str = json.dumps(metadata or {}, ensure_ascii=False)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO knowledge_items (expert, domain, topic, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (self.name, self.domain, topic.strip(), content.strip(), meta_str))
            conn.commit()
            return cursor.lastrowid

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Busca conocimientos relevantes dentro del dominio de este experto usando tokens flexibles."""
        # Limpiar palabras irrelevantes comunes
        stop_words = {"como", "cómo", "de", "la", "el", "en", "con", "un", "una", "los", "las", "para", "por", "que", "qué"}
        tokens = [t.strip().lower() for t in query.split() if t.strip().lower() not in stop_words and len(t.strip()) > 1]
        
        if not tokens:
            tokens = [query.strip().lower()]

        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Construir condición OR para tokens significativos
            conditions = []
            params = [self.name]
            for tok in tokens:
                conditions.append("(LOWER(topic) LIKE ? OR LOWER(content) LIKE ?)")
                params.extend([f"%{tok}%", f"%{tok}%"])
                
            where_clause = " OR ".join(conditions)
            query_sql = f"""
                SELECT id, topic, content, metadata, created_at 
                FROM knowledge_items
                WHERE expert = ? AND ({where_clause})
                ORDER BY id DESC
                LIMIT ?
            """
            params.append(limit)
            cursor.execute(query_sql, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]


    def get_all_topics(self) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT topic FROM knowledge_items WHERE expert = ? ORDER BY topic
            """, (self.name,))
            return [r[0] for r in cursor.fetchall()]

    def count_knowledge(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM knowledge_items WHERE expert = ?", (self.name,))
            return cursor.fetchone()[0]
