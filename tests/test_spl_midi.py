# Author: Tresslers Group
import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from SessionProducerPro.spl_integration.midi_generator_v2 import MidiGeneratorV2, MidiNote, MidiCC

class TestSplMidiGeneratorV2(unittest.TestCase):
    def setUp(self):
        self.gen = MidiGeneratorV2()

    def test_expressive_cc_generation(self):
        # Test pad generation which should now include CC sweeps
        intent = {
            "instrument_type": "strings",
            "key": "A minor",
            "bars": 4
        }
        
        notes, ccs = self.gen.generate_sequence(intent, energy=0.8)
        
        # Should generate both notes and continuous CC data
        self.assertTrue(len(notes) > 0, "No notes generated for strings.")
        self.assertTrue(len(ccs) > 0, "No CC data generated for expressive strings.")
        
        # Verify both CC1 (Mod Wheel) and CC11 (Expression) are present
        cc_types = set([cc.control for cc in ccs])
        self.assertIn(1, cc_types, "CC1 (Modulation Wheel) missing.")
        self.assertIn(11, cc_types, "CC11 (Expression) missing.")
        
        # Check that CCs have dynamic values (not all the same)
        cc1_vals = [cc.value for cc in ccs if cc.control == 1]
        self.assertTrue(len(set(cc1_vals)) > 1, "CC1 values are completely static, no swell generated.")

    def test_pluck_generation_no_ccs(self):
        # Test pluck generation which should NOT include CC sweeps
        intent = {
            "instrument_type": "pluck",
            "key": "A minor",
            "bars": 2
        }
        
        notes, ccs = self.gen.generate_sequence(intent, energy=0.5)
        
        self.assertTrue(len(notes) > 0, "No notes generated for pluck.")
        # Plucks don't get the CC swells in the current design
        self.assertEqual(len(ccs), 0, "CC data generated for a pluck instrument when it shouldn't be.")

if __name__ == '__main__':
    unittest.main()

