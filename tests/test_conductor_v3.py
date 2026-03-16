# Author: Tresslers Group

import unittest
from production_engine.arrangement_engine import ArrangementEngine
from ai.strategy_engine import StrategyEngine
from ai.intent_classifier import Intent

class TestConductorV3(unittest.TestCase):
    def setUp(self):
        self.arr_eng = ArrangementEngine()
        self.strategy_eng = StrategyEngine(arrangement_engine=self.arr_eng)

    def test_epic_fantasy_archetype_selection(self):
        # Test that 'fantasy' or 'epic' triggers the Epic Fantasy structure
        arr = self.arr_eng.generate_cinematic_arrangement(mood="Epic Fantasy", key="D")
        
        # Epic Fantasy has 5 sections: Intro, Exploration, Tension, Battle, Resolution
        self.assertEqual(len(arr.sections), 5)
        self.assertEqual(arr.sections[0].name, "Intro (Ancient Darkness)")
        self.assertEqual(arr.sections[3].name, "Battle Climax (Wraith)")
        self.assertEqual(arr.sections[3].energy, 1.0)
        
        # Verify heavy layering in Battle Climax
        battle_strategies = [s for s in arr.strategies if s['parameters'].get('start_bar', 0) >= 40]
        # Intro(8) + Exploration(16) + Tension(16) = 40 bars
        self.assertTrue(len(battle_strategies) >= 3)
        
    def test_incremental_tempo_and_dynamic_curve(self):
        arr = self.arr_eng.generate_cinematic_arrangement(mood="fantasy", key="D")
        
        # Battle Climax starts at bar 40 (8 Intro + 16 Exploration + 16 Tension)
        battle_chords = next(s for s in arr.strategies if s['parameters'].get('start_bar') == 40 and s['type'] == 'chord_generation')
        self.assertEqual(battle_chords['parameters'].get('dynamic_curve'), 'dramatic')

    def test_temporal_alignment_logic(self):
        arr = self.arr_eng.generate_cinematic_arrangement(mood="fantasy", key="D")
        
        # Verify that we have strategies starting at bar 40
        battle_start_bars = [s['parameters'].get('start_bar') for s in arr.strategies]
        self.assertIn(40, battle_start_bars)
        
        # Verify specific instrument in the battle section
        battle_instruments = [s['parameters'].get('instrument') for s in arr.strategies if s['parameters'].get('start_bar') == 40]
        self.assertIn("Low Orchestral Brass", battle_instruments)

if __name__ == '__main__':
    unittest.main()

