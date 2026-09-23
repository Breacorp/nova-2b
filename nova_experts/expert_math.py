from .base_expert import BaseExpert

class MathExpert(BaseExpert):
    """
    Experto en Matemáticas, Álgebra, Lógica y Cálculo de Nova AI.
    Especialidades: Álgebra lineal, resolución de ecuaciones, cálculo diferencial y estadística.
    """
    def __init__(self, db_path: str = None):
        kwargs = {"db_path": db_path} if db_path else {}
        super().__init__(name="MathExpert", domain="mathematics", **kwargs)
        self._seed_initial_knowledge()

    def _seed_initial_knowledge(self):
        if self.count_knowledge() > 0:
            return

        initial_seeds = [
            (
                "Álgebra: Fórmula Cuadrática General",
                "Para toda ecuación de la forma ax² + bx + c = 0:\n"
                "x = (-b ± √(b² - 4ac)) / (2a)\n"
                "Discriminante Δ = b² - 4ac:\n"
                "- Δ > 0: dos soluciones reales distintas.\n"
                "- Δ = 0: una solución real doble.\n"
                "- Δ < 0: dos soluciones complejas conjugadas.",
                {"field": "algebra", "type": "formula"}
            ),
            (
                "Álgebra Lineal: Multiplicación de Matrices y Determinantes",
                "Para multiplicar A (m x n) por B (n x p), el resultado C es (m x p), donde:\n"
                "C[i][j] = Σ (A[i][k] * B[k][j]) para k=1..n.\n"
                "Propiedades clave de determinantes:\n"
                "- det(AB) = det(A) * det(B)\n"
                "- det(A⁻¹) = 1 / det(A) (si det(A) ≠ 0)\n"
                "- det(Aᵀ) = det(A)",
                {"field": "linear_algebra", "type": "theory"}
            ),
            (
                "Cálculo: Regla de la Cadena y Derivadas Fundamentales",
                "Regla de la cadena: (f(g(x)))' = f'(g(x)) * g'(x)\n"
                "Derivadas básicas:\n"
                "- d/dx [xⁿ] = n * xⁿ⁻¹\n"
                "- d/dx [eˣ] = eˣ\n"
                "- d/dx [ln(x)] = 1/x\n"
                "- d/dx [sin(x)] = cos(x)\n"
                "- d/dx [cos(x)] = -sin(x)",
                {"field": "calculus", "type": "rules"}
            ),
            (
                "Estadística: Teorema del Límite Central (TLC)",
                "Dadas n variables aleatorias independientes e idénticamente distribuidas (i.i.d.) con media μ y varianza σ² < ∞:\n"
                "A medida que n → ∞, la distribución de la media muestral estandarizada converge hacia una distribución normal estándar N(0, 1).",
                {"field": "statistics", "type": "theorem"}
            )
        ]

        for topic, content, meta in initial_seeds:
            self.learn(topic, content, meta)
