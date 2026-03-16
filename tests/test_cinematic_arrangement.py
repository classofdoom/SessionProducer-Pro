# Author: Tresslers Group

import unittest
from production_engine.arrangement_engine import ArrangementEngine
from ai.strategy_engine import StrategyEngine, ProductionStrategy
from ai.intent_classifier import Intent
from types import SimpleNamespace

class TestCinematicArrangement(unittest.TestCase):
    def setUp(self):
        self.arr_eng = ArrangementEngine()
        self.strategy_eng = StrategyEngine(arrangement_engine=self.arr_eng)

    def test_arrangement_generation_logic(self):
        # 1. Test the Engine directly
        arr = self.arr_eng.generate_cinematic_arrangement(mood="dark", key="D")
        self.assertEqual(len(arr.sections), 4)
        self.assertEqual(arr.sections[0].scale, "phrygian")
        # Ensure strategies are generated
        self.assertTrue(len(arr.strategies) >= 4)
        # Check for start_bar staggered logic
        self.assertEqual(arr.strategies[0]['parameters']['start_bar'], 0)
        
    def test_strategy_engine_integration(self):
        # 2. Test Delegation from StrategyEngine
        intent = Intent(
            category="arrangement", 
            sub_action="create_cinematic", 
            target_tracks=[],
            parameters={"key": "E"},
            confidence=1.0,
            raw_text="Gimme a dark tension building cinematic structure in E phrygian"
        )
        
        strategy = self.strategy_eng.develop_strategy(intent)
        
        self.assertEqual(strategy.intent.category, "arrangement")
        self.assertTrue(len(strategy.strategies) > 0)
        self.assertIn("Orchestrating a full 'dark' cinematic structure", strategy.reasoning)
        
        # Verify first strategy block
        first_move = strategy.strategies[0]
        self.assertEqual(first_move['parameters']['scale'], "E phrygian")

if __name__ == '__main__':
    unittest.main()

