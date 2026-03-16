# Author: Tresslers Group

import unittest
from spl_integration.theory_engine import TheoryEngine
from spl_integration.midi_generator_v2 import MidiGeneratorV2

class TestCinematicIntelligence(unittest.TestCase):
    def setUp(self):
        self.theory = TheoryEngine()
        self.midi = MidiGeneratorV2()

    def test_phrygian_scale(self):
        # Phrygian should have a minor second (b2)
        print(f"Available scales: {self.theory.scales.keys()}")
        scale = self.theory.get_scale_notes("E", "phrygian")
        print(f"E Phrygian notes: {scale}")
        # E Phrygian: E, F, G, A, B, C, D
        self.assertEqual(scale[1] - scale[0], 1) # F is 1 semitone above E

    def test_power_chord(self):
        # Power chord should be 1, 5, 8
        chord = self.theory.get_chord_notes("C", "power", octave=4)
        # 60 (C4), 67 (G4), 72 (C5)
        self.assertEqual(chord, [60, 67, 72])

    def test_cinematic_pulse_generation(self):
        # Test pulse routing
        intent = {
            "instrument_type": "strings",
            "pattern": "pulse",
            "scale": "A minor",
            "bars": 4
        }
        notes, _ = self.midi.generate_sequence(intent, energy=0.8)
        self.assertTrue(len(notes) > 0)
        # Check for 16th notes (0.25 duration/step) - account for jitter
        self.assertAlmostEqual(notes[1].start_time - notes[0].start_time, 0.25, delta=0.05)

    def test_ritualistic_drum_pattern(self):
        # Test ritualistic drum pattern
        intent = {
            "instrument_type": "percussion",
            "pattern": "ritualistic",
            "bars": 4
        }
        notes, _ = self.midi.generate_sequence(intent, energy=0.7)
        self.assertTrue(len(notes) > 0)
        # Ensure toms were used
        pitches = [n.pitch for n in notes]
        self.assertTrue(any(p in [41, 43, 45] for p in pitches))

if __name__ == '__main__':
    unittest.main()

