import os
import re
from typing import Dict, Any, List
from nova_experts import CodeExpert, LanguagesExpert, MathExpert
from nova_rag import NovaRAG

class NovaAssimilator:
    """
    Motor de asimilación de conocimiento continuo para Nova AI.
    Permite ingerir manuales, textos, documentación técnica o snippets (.txt, .md, .py, .js, .html, .css),
    clasificándolos e indexándolos tanto en el Experto correspondiente como en el índice RAG FTS5.
    """
    def __init__(self, code_expert: CodeExpert, lang_expert: LanguagesExpert, math_expert: MathExpert, rag: NovaRAG = None):
        self.code_expert = code_expert
        self.lang_expert = lang_expert
        self.math_expert = math_expert
        self.rag = rag or NovaRAG()


    def route_knowledge(self, topic: str, content: str, hint_domain: str = None):
        """Determina qué experto debe almacenar el nuevo conocimiento."""
        text = f"{topic} {content}".lower()
        
        if hint_domain:
            hint = hint_domain.lower()
            if "code" in hint or "program" in hint or "css" in hint or "html" in hint or "python" in hint or "js" in hint:
                return self.code_expert
            if "lang" in hint or "idioma" in hint or "traducc" in hint:
                return self.lang_expert
            if "math" in hint or "matemat" in hint or "algeb" in hint or "calcul" in hint:
                return self.math_expert

        # Detección por patrones y palabras clave
        code_keywords = ["python", "javascript", "html", "css", "function", "class", "async", "def ", "var ", "const ", "let ", "div", "style"]
        math_keywords = ["ecuacion", "álgebra", "algebra", "matematica", "matemática", "integral", "derivada", "teorema", "formula", "fórmula", "matriz", "vector"]
        lang_keywords = ["idioma", "chino", "mandarín", "mandarin", "francés", "frances", "portugués", "portugues", "inglés", "ingles", "español", "gramatica", "gramática", "vocabulario"]

        code_score = sum(1 for kw in code_keywords if kw in text)
        math_score = sum(1 for kw in math_keywords if kw in text)
        lang_score = sum(1 for kw in lang_keywords if kw in text)

        scores = [
            (code_score, self.code_expert),
            (math_score, self.math_expert),
            (lang_score, self.lang_expert)
        ]
        scores.sort(key=lambda x: x[0], reverse=True)

        # Si no encaja claro en uno de los tres especializados, usa code_expert o el de mayor puntaje
        best_match = scores[0][1] if scores[0][0] > 0 else self.code_expert
        return best_match

    def assimilate_entry(self, topic: str, content: str, domain: str = None, metadata: Dict[str, Any] = None):
        """Asimila un hecho o conocimiento puntual y lo indexa en el experto y en RAG FTS5."""
        expert = self.route_knowledge(topic, content, domain)
        entry_id = expert.learn(topic, content, metadata)
        # Sincronización en RAG FTS5
        self.rag.add_document(title=topic, content=content, source=expert.name, category=domain or expert.domain)
        return {
            "status": "success",
            "expert": expert.name,
            "topic": topic,
            "entry_id": entry_id
        }


    def ingest_file(self, file_path: str, domain_hint: str = None) -> List[Dict[str, Any]]:
        """Ingiere un manual, archivo de texto o markdown y lo descompone en lecciones/conocimientos."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        base_name = os.path.basename(file_path)
        # Separar por encabezados Markdown o secciones
        sections = re.split(r'\n(?=#{1,3}\s+)', text)
        assimilated = []

        if len(sections) <= 1:
            # Archivo sin encabezados, asimilar completo
            res = self.assimilate_entry(topic=f"Doc: {base_name}", content=text, domain=domain_hint, metadata={"source": file_path})
            assimilated.append(res)
        else:
            for section in sections:
                clean_sec = section.strip()
                if not clean_sec:
                    continue
                lines = clean_sec.splitlines()
                first_line = lines[0].lstrip("#").strip()
                topic_title = f"[{base_name}] {first_line[:80]}"
                content_body = "\n".join(lines[1:]).strip() if len(lines) > 1 else clean_sec
                res = self.assimilate_entry(topic=topic_title, content=content_body, domain=domain_hint, metadata={"source": file_path})
                assimilated.append(res)

        return assimilated
