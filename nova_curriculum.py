import random
from typing import Dict, Any, List, Tuple

class CurriculumGenerator:
    """
    Generador de Currículum y Pruebas Sintéticas para Nova AI.
    Genera problemas de práctica específicos para atacar debilidades diagnosticadas.
    """
    def generate_practice_batch(self, skill_name: str, count: int = 10) -> List[Dict[str, Any]]:
        """Genera un lote de ejercicios con su respuesta esperada matemáticamente verificada."""
        batch = []
        if "arithmetic" in skill_name or "word_problem" in skill_name or "math" in skill_name:
            names = ["Juan", "Pedro", "Ana", "Lucía", "Carlos", "María"]
            items = ["manzanas", "naranjas", "caramelos", "libros", "figuras"]

            for i in range(count):
                p1 = random.choice(names)
                p2 = random.choice([n for n in names if n != p1])
                it = random.choice(items)
                
                initial = random.randint(5, 20)
                give = random.randint(1, initial - 2)
                return_back = random.randint(1, 4)
                
                # Ejemplo: Juan tiene X. Le da Y a Pedro. Pedro le devuelve Z. ¿Cuántos tiene Juan?
                # Total = X - Y + Z
                expected = initial - give + return_back
                prompt = (
                    f"{p1} tiene {initial} {it}. Le da {give} a {p2}. "
                    f"Luego {p2} le devuelve {return_back}. ¿Cuántas {it} tiene {p1} al final?"
                )
                
                batch.append({
                    "id": i + 1,
                    "skill": skill_name,
                    "prompt": prompt,
                    "expected": expected,
                    "verification_formula": f"{initial} - {give} + {return_back}"
                })
        elif "css" in skill_name or "code" in skill_name:
            code_drills = [
                ("CSS: Centrar vertical y horizontal con Grid", "display: grid; place-items: center;", "place-items: center"),
                ("Python: Abrir archivo con context manager", "with open('f.txt', 'r') as f: content = f.read()", "with open"),
                ("JS: Declarar función flecha asíncrona", "const getData = async () => await fetch(url);", "async")
            ]
            for i in range(count):
                drill = random.choice(code_drills)
                batch.append({
                    "id": i + 1,
                    "skill": skill_name,
                    "prompt": drill[0],
                    "expected": drill[1],
                    "verification_formula": drill[2]
                })
        else:
            # Caso genérico
            batch.append({
                "id": 1,
                "skill": skill_name,
                "prompt": f"Práctica sobre {skill_name}",
                "expected": "Válido",
                "verification_formula": "standard_check"
            })

        return batch
