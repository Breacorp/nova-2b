from .base_expert import BaseExpert

class LanguagesExpert(BaseExpert):
    """
    Experto Políglota y Lingüístico de Nova AI.
    Especialidades: Chino (Mandarín), Inglés, Francés, Portugués, Español.
    Gramática comparada, modismos y traducción contextual.
    """
    def __init__(self, db_path: str = None):
        kwargs = {"db_path": db_path} if db_path else {}
        super().__init__(name="LanguagesExpert", domain="linguistics", **kwargs)
        self._seed_initial_knowledge()

    def _seed_initial_knowledge(self):
        if self.count_knowledge() > 0:
            return

        initial_seeds = [
            (
                "Mandarín: Estructura de Oración Básica (SVO + Tiempo/Lugar)",
                "En Chino Mandarín el orden estándar es: Sujeto + Tiempo + Lugar + Verbo + Objeto.\n"
                "Ejemplo: 我今天在图书馆看书 (Wǒ jīntiān zài túshūguǎn kàn shū) -> 'Yo hoy en la biblioteca leo un libro'.\n"
                "No hay conjugación verbal ni concordancia de género/número.",
                {"language": "chinese", "level": "grammar"}
            ),
            (
                "Inglés vs Español: Tiempos Perfectos y Falsos Amigos",
                "Present Perfect en Inglés ('I have lived here for 2 years') equivale en Español a 'Vivo aquí desde hace 2 años'.\n"
                "Falsos amigos clave:\n"
                "- Actually = En realidad (NO actualmente -> currently)\n"
                "- Eventually = Con el tiempo / finalmente (NO eventualmente -> occasionally)\n"
                "- Realize = Darse cuenta (NO realizar -> perform/carry out)",
                {"languages": ["english", "spanish"], "level": "vocabulary"}
            ),
            (
                "Francés: Concordancia del Participe Passé",
                "Con el auxiliar 'être', el participio concuerda en género y número con el sujeto: 'Elles sont arrivées'.\n"
                "Con el auxiliar 'avoir', solo concuerda si el COD precede al verbo: 'Les fleurs que j'ai vues'.",
                {"language": "french", "level": "grammar"}
            ),
            (
                "Portugués: Uso del Infinitivo Personal (Infinitivo Pessoal)",
                "El portugués tiene un infinitivo conjugable único en lenguas romances:\n"
                "Para eu fazer, para tu fazeres, para ele fazer, para nós fazermos, para vós fazerdes, para eles fazerem.\n"
                "Permite expresar el sujeto de una acción subordinada sin recurrir obligatoriamente al subjuntivo.",
                {"language": "portuguese", "level": "grammar"}
            )
        ]

        for topic, content, meta in initial_seeds:
            self.learn(topic, content, meta)
