# Author: Tresslers Group
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class TheoryEngine:
    """
    The 'Musical Brain' of SessionProducer Pro.
    Handles chord spelling, scales, and professional voicings.
    """
    def __init__(self):
        self.intervals = {
            "1": 0, "b2": 1, "2": 2, "#2": 3, "b3": 3, "3": 4, "4": 5,
            "#4": 6, "b5": 6, "5": 7, "#5": 8, "b6": 8, "6": 9, "b7": 10, "7": 11,
            "b9": 13, "9": 14, "#9": 15, "11": 17, "#11": 18, "b13": 20, "13": 21
        }
        
        self.scales = {
            "major": [0, 2, 4, 5, 7, 9, 11],
            "minor": [0, 2, 3, 5, 7, 8, 10],
            "dorian": [0, 2, 3, 5, 7, 9, 10],
            "phrygian": [0, 1, 3, 5, 7, 8, 10],
            "lydian": [0, 2, 4, 6, 7, 9, 11],
            "mixolydian": [0, 2, 4, 5, 7, 9, 10],
            "locrian": [0, 1, 3, 5, 6, 8, 10],
            "harmonic minor": [0, 2, 3, 5, 7, 8, 11],
            "melodic minor": [0, 2, 3, 5, 7, 9, 11],
            "h_minor": [0, 2, 3, 5, 7, 8, 11],
            "m_minor": [0, 2, 3, 5, 7, 9, 11],
            "maj_pent": [0, 2, 4, 7, 9],
            "min_pent": [0, 3, 5, 7, 10]
        }
        
        self.roots = {
            "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, 
            "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, 
            "A#": 10, "Bb": 10, "B": 11
        }

    def get_chord_notes(self, root: str, chord_type: str, octave: int = 4) -> List[int]:
        """
        Parses a chord type (e.g. 'maj7', 'min9', 'sus4') and returns MIDI notes.
        """
        root_midi = (octave + 1) * 12 + self.roots.get(root, 0)
        
        # Chord definitions relative to root
        recipes = {
            "maj": [0, 4, 7],
            "min": [0, 3, 7],
            "dim": [0, 3, 6],
            "aug": [0, 4, 8],
            "maj7": [0, 4, 7, 11],
            "min7": [0, 3, 7, 10],
            "7": [0, 4, 7, 10],
            "min7b5": [0, 3, 6, 10],
            "maj9": [0, 4, 7, 11, 14],
            "min9": [0, 3, 7, 10, 14],
            "min9": [0, 3, 7, 10, 14],
            "sus2": [0, 2, 7],
            "sus4": [0, 5, 7],
            "add9": [0, 4, 7, 14],
            "69": [0, 4, 7, 9, 14],
            "power": [0, 7, 12],
            "octave": [0, 12]
        }
        
        offsets = recipes.get(chord_type.lower(), [0, 4, 7])
        return [root_midi + o for o in offsets]

    def get_voice_led_chord(self, target_root: str, target_type: str, prev_notes: List[int]) -> List[int]:
        """
        Selects an inversion of the target chord that is closest to the previous notes.
        This creates professional, flowing transitions.
        """
        if not prev_notes:
            return self.get_chord_notes(target_root, target_type)

        avg_prev = sum(prev_notes) / len(prev_notes)
        
        # Get base notes in a reasonable range
        base_notes = self.get_chord_notes(target_root, target_type, octave=int(avg_prev // 12) - 1)
        
        # Generate possible inversions/octave shifts
        best_voicings = []
        for shift in [-12, 0, 12]:
            shifted = [n + shift for n in base_notes]
            avg_shifted = sum(shifted) / len(shifted)
            dist = abs(avg_shifted - avg_prev)
            best_voicings.append((dist, shifted))
            
        # Return the one with minimum distance to center of previous chord
        best_voicings.sort(key=lambda x: x[0])
        return sorted(best_voicings[0][1])

    def get_scale_notes(self, root: str, scale_type: str, octaves: int = 1, start_octave: int = 4) -> List[int]:
        root_midi = (start_octave + 1) * 12 + self.roots.get(root, 0)
        intervals = self.scales.get(scale_type.lower(), self.scales["major"])
        
        notes = []
        for o in range(octaves):
            for i in intervals:
                notes.append(root_midi + i + (o * 12))
        return notes

    def get_diatonic_chords(self, root: str, scale_type: str) -> List[Dict[str, str]]:
        """
        Returns the 7 diatonic chords for a given scale.
        """
        s_lower = scale_type.lower()
        if s_lower == "major":
            return [
                {"degree": "I", "type": "maj7"},
                {"degree": "ii", "type": "min7"},
                {"degree": "iii", "type": "min7"},
                {"degree": "IV", "type": "maj7"},
                {"degree": "V", "type": "7"},
                {"degree": "vi", "type": "min7"},
                {"degree": "vii", "type": "min7b5"}
            ]
        elif "minor" in s_lower or s_lower == "aeolian":
             return [
                {"degree": "i", "type": "min7"},
                {"degree": "ii", "type": "min7b5"},
                {"degree": "III", "type": "maj7"},
                {"degree": "iv", "type": "min7"},
                {"degree": "v", "type": "min7"},
                {"degree": "VI", "type": "maj7"},
                {"degree": "VII", "type": "7"}
            ]
        return [{"degree": "I", "type": "maj"}]

