import sqlite3
import os
import re
from typing import List, Dict, Any

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "knowledge.db")

class NovaRAG:
    """
    Motor RAG ultraligero basado en SQLite + FTS5 (Full-Text Search 5).
    Indexa y recupera fragmentos de documentos (PDF/TXT/MD/Código) sin dependencias pesadas ni vectores.
    """
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_fts()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_fts(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Tabla FTS5 para búsqueda ultrarrápida por tokens y relevancia BM25
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS rag_documents USING fts5(
                    title,
                    content,
                    source,
                    category,
                    tokenize='porter unicode61'
                )
            """)
            conn.commit()

    def add_document(self, title: str, content: str, source: str = "manual", category: str = "general") -> None:
        """Agrega o indexa un documento o fragmento en el índice FTS5."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO rag_documents (title, content, source, category)
                VALUES (?, ?, ?, ?)
            """, (title.strip(), content.strip(), source.strip(), category.strip()))
            conn.commit()

    def search(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        """
        Búsqueda de texto completo con ranking nativo BM25 de SQLite FTS5.
        """
        clean_q = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]', ' ', query).strip()
        tokens = [t for t in clean_q.split() if len(t) > 2]
        if not tokens:
            return []

        fts_query = " OR ".join([f'"{t}"*' for t in tokens])

        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT title, content, source, category, bm25(rag_documents) as score
                    FROM rag_documents
                    WHERE rag_documents MATCH ?
                    ORDER BY score
                    LIMIT ?
                """, (fts_query, limit))
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
            except sqlite3.OperationalError:
                # Fallback si la sintaxis FTS5 compleja falla
                cursor.execute("""
                    SELECT title, content, source, category, 0.0 as score
                    FROM rag_documents
                    WHERE content LIKE ? OR title LIKE ?
                    LIMIT ?
                """, (f"%{clean_q}%", f"%{clean_q}%", limit))
                return [dict(r) for r in cursor.fetchall()]

    def count_documents(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM rag_documents")
            return cursor.fetchone()[0]
