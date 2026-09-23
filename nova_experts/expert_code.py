from .base_expert import BaseExpert

class CodeExpert(BaseExpert):
    """
    Experto en Programación y Desarrollo de Software.
    Especialidades: Python, JavaScript/TypeScript, HTML5, CSS3 y Arquitectura de Software.
    """
    def __init__(self, db_path: str = None):
        kwargs = {"db_path": db_path} if db_path else {}
        super().__init__(name="CodeExpert", domain="programming", **kwargs)
        self._seed_initial_knowledge()

    def _seed_initial_knowledge(self):
        """Carga conocimientos iniciales fundamentales si la base de datos está vacía."""
        if self.count_knowledge() > 0:
            return

        initial_seeds = [
            (
                "CSS: Centrado Absoluto y Flexbox",
                "Para centrar un elemento en CSS usando Flexbox:\n"
                "display: flex;\njustify-content: center;\nalign-items: center;\n"
                "O con CSS Grid: display: grid; place-items: center;",
                {"language": "css", "category": "layout"}
            ),
            (
                "HTML5: Estructura Semántica Moderna",
                "Estructura estándar HTML5:\n"
                "<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n  <meta charset=\"UTF-8\">\n  "
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n  "
                "<title>Nova App</title>\n</head>\n<body>\n  <header></header>\n  <main></main>\n  "
                "<footer></footer>\n</body>\n</html>",
                {"language": "html", "category": "semantics"}
            ),
            (
                "JavaScript: Fetch API Asíncrono con Manejo de Errores",
                "async function fetchData(url) {\n  try {\n    const response = await fetch(url);\n    "
                "if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);\n    "
                "return await response.json();\n  } catch (err) {\n    console.error('Fetch error:', err);\n    "
                "throw err;\n  }\n}",
                {"language": "javascript", "category": "network"}
            ),
            (
                "Python: Context Managers y Buenas Prácticas",
                "Uso idiomático de context manager en Python para manejo de recursos:\n"
                "with open('archivo.txt', 'r', encoding='utf-8') as f:\n    contenido = f.read()\n"
                "Garantiza el cierre automático del descriptor de archivo aún ante excepciones.",
                {"language": "python", "category": "best-practices"}
            ),
            (
                "Python: List & Dict Comprehensions",
                "# Filtrado y mapeo eficiente en Python:\n"
                "cuadrados_pares = [x**2 for x in range(20) if x % 2 == 0]\n"
                "lookup_dict = {item['id']: item['nombre'] for item in items}",
                {"language": "python", "category": "syntax"}
            )
        ]

        for topic, content, meta in initial_seeds:
            self.learn(topic, content, meta)
