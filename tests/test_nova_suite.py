import unittest
import os
import shutil

from nova_memory import UserMemory
from nova_rag import NovaRAG
from nova_learning import LearningEngine
from nova_experts import CodeExpert, LanguagesExpert, MathExpert
from nova_assimilator import NovaAssimilator
from nova_router import HybridRouter
from nova_core import NovaCore
from nova_native import pack_ternary, unpack_ternary, dot_product_ternary, integer_accuracy
from nova_evaluator import SkillProfileManager
from nova_gap_detector import GapDetector
from nova_curiosity import CuriosityEngine
from nova_curriculum import CurriculumGenerator
from nova_verifier import VerificationEngine
from nova_learning_planner import LearningPlanner
from nova_self_improve import SelfImprovementEngine
from nova_runtime import NovaRuntime
from nova_gguf import NovaGGUFInspector

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_knowledge.db")

class TestNovaAIFullSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    def test_1_user_memory(self):
        mem = UserMemory(db_path=TEST_DB_PATH)
        mem.set("mascota", "Átomo", category="personal")
        self.assertEqual(mem.get("mascota"), "Átomo")
        res = mem.search("mascota")
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0]["value"], "Átomo")

    def test_2_rag_fts5(self):
        rag = NovaRAG(db_path=TEST_DB_PATH)
        rag.add_document("Arquitectura Microkernel", "ModernOS utiliza microkernel con comunicación IPC", "test_doc", "systems")
        hits = rag.search("microkernel IPC")
        self.assertTrue(len(hits) > 0)
        self.assertIn("ModernOS", hits[0]["content"])

    def test_3_moce_experts(self):
        code_exp = CodeExpert(db_path=TEST_DB_PATH)
        self.assertTrue(code_exp.count_knowledge() >= 5)
        res = code_exp.search("Flexbox")
        self.assertTrue(len(res) > 0)

        math_exp = MathExpert(db_path=TEST_DB_PATH)
        self.assertTrue(math_exp.count_knowledge() >= 4)
        res_math = math_exp.search("cuadrática")
        self.assertTrue(len(res_math) > 0)

    def test_4_hybrid_router_and_core(self):
        core = NovaCore(db_path=TEST_DB_PATH)
        greeting = core.ask("Hola")
        self.assertTrue(greeting["resolved"])
        self.assertIn("Nova AI", greeting["response"])

        mem_save = core.ask("Mi perro se llama Átomo")
        self.assertTrue(mem_save["resolved"])

        mem_query = core.ask("¿Cómo se llama mi perro?")
        self.assertTrue(mem_query["resolved"])
        self.assertIn("Átomo", mem_query["response"])

    def test_5_self_improvement_cycle(self):
        core = NovaCore(db_path=TEST_DB_PATH)
        # Forzar debilidad
        core.gap_detector.analyze_failure(
            domain="mathematics",
            skill="arithmetic_word_problems",
            input_prompt="Juan tiene 7 manzanas...",
            expected=5,
            generated=4
        )
        gaps = core.gap_detector.find_active_gaps()
        self.assertTrue(len(gaps) > 0)

        cycle = core.self_improve.run_self_improvement_cycle()
        self.assertEqual(cycle["cycle_status"], "COMPLETED")
        self.assertEqual(cycle["outcome"], "PASS_CONSOLIDATE")

    def test_6_nova_native_ternary(self):
        weights = [-1, 0, 1, 1, 0, -1, 1, 0]
        packed = pack_ternary(weights)
        self.assertEqual(len(packed), 2)  # 8 pesos en 2 bytes
        unpacked = unpack_ternary(packed, 8)
        self.assertEqual(weights, unpacked)

        activations = [10, 20, 30, 40, 50, 60, 70, 80]
        # -10 + 0 + 30 + 40 + 0 - 60 + 70 + 0 = 70
        acc = dot_product_ternary(packed, 8, activations)
        self.assertEqual(acc, 70)

        acc_pct = integer_accuracy(95, 100)
        self.assertEqual(acc_pct, 950)

    def test_7_runtime_and_gguf_inspector(self):
        runtime = NovaRuntime(dev_mode=True)
        status = runtime.get_status()
        self.assertEqual(status["model"], "Nova 2B")
        self.assertEqual(status["status"], "Connected")

        api_res = runtime.chat_completion_api([{"role": "user", "content": "Hola"}])
        self.assertIn("choices", api_res)
        self.assertEqual(api_res["choices"][0]["message"]["role"], "assistant")

        inspector = NovaGGUFInspector("nova-2b.gguf")
        meta = inspector.inspect_metadata()
        self.assertEqual(meta["nova.version"], "2.0.0")
        self.assertEqual(meta["nova.author"], "ModernoTech")

if __name__ == "__main__":
    unittest.main()
