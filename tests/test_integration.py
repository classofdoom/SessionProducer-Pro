# Author: Tresslers Group

import sys
import os
import unittest

# Add project root and source root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'SessionProducerPro')))

from SessionProducerPro.asset_engine.asset_indexer import AssetIndexer
from SessionProducerPro.asset_engine.asset_matcher import AssetMatcher
from SessionProducerPro.production_engine.midi_generator import MidiGenerator
from SessionProducerPro.production_engine.arrangement_engine import ArrangementEngine
from SessionProducerPro.reaper_bridge.command_writer import CommandWriter
from SessionProducerPro.ai.mode_router import ModeRouter

class TestIntegration(unittest.TestCase):
    def test_component_instantiation(self):
        # 1. Asset Engine
        indexer = AssetIndexer(":memory:") # Use in-memory DB for test
        matcher = AssetMatcher(":memory:")
        self.assertIsNotNone(indexer)
        self.assertIsNotNone(matcher)
        
        # 2. Production Engine
        midi_gen = MidiGenerator()
        arr_eng = ArrangementEngine()
        drums = midi_gen.generate_drum_pattern()
        self.assertTrue(len(drums) > 0)
        
        # 3. Reaper Bridge
        writer = CommandWriter()
        
        # Test basic command sending - we can't fully test WebRC without REAPER running,
        # but we can ensure the class initialized without error.
        self.assertIsNotNone(writer.reaper)
        
        # 4. AI
        router = ModeRouter()
        intent = router.classify("generate drum track")
        self.assertEqual(intent.action, "generate_drums")

if __name__ == '__main__':
    unittest.main()

