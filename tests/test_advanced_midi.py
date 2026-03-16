# Author: Tresslers Group
import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SessionProducerPro.spl_integration.theory_engine import TheoryEngine
from SessionProducerPro.spl_integration.midi_generator_v2 import MidiGeneratorV2

class TestAdvancedMidi(unittest.TestCase):
    def setUp(self):
        self.theory = TheoryEngine()
        self.gen = MidiGeneratorV2()

    def test_voice_leading_proximity(self):
        """Verify that voice leading chooses closer notes than standard block chords."""
        # Previous chord: C Major (C4, E4, G4) -> (60, 64, 67)
        prev_notes = [60, 64, 67]
        
        # Target: F Major
        # Standard block F4 (65, 69, 72)
        # Voice led would likely be F4 - A4 - C4 (inverse) or similar to keep notes close
        led_chord = self.theory.get_voice_led_chord("F", "maj", prev_notes)
        
        avg_prev = sum(prev_notes) / len(prev_notes)
        avg_led = sum(led_chord) / len(led_chord)
        
        print(f"Prev Avg: {avg_prev}, Led Avg: {avg_led}, Led Chord: {led_chord}")
        
        # The average distance should be small (< 6 semitones usually)
        self.assertLess(abs(avg_prev - avg_led), 6)

    def test_arpeggio_generation(self):
        """Verify arpeggio generates expected notes from scale."""
        intent = {
            "instrument_type": "pluck",
            "pattern": "arpeggio",
            "key": "C major",
            "bars": 1
        }
        notes, _ = self.gen.generate_sequence(intent, energy=0.5)
        
        self.assertTrue(len(notes) > 0)
        # All notes should be in C major (0, 2, 4, 5, 7, 9, 11)
        for n in notes:
            self.assertIn(n.pitch % 12, [0, 2, 4, 5, 7, 9, 11])

    def test_melody_variation(self):
        """Verify melody generator produces different notes across bars."""
        intent = {
            "instrument_type": "keys",
            "pattern": "melody",
            "key": "A minor",
            "bars": 4
        }
        notes, _ = self.gen.generate_sequence(intent, energy=0.8)
        
        # Check if pitches vary
        pitches = [n.pitch for n in notes]
        self.assertGreater(len(set(pitches)), 1)

if __name__ == '__main__':
    unittest.main()

