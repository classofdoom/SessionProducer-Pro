# Author: Tresslers Group

import random
from dataclasses import dataclass
from typing import List, Tuple, Dict

@dataclass
class MidiNote:
    pitch: int
    velocity: int
    start_time: float # in beats
    duration: float   # in beats

class MidiGenerator:
    """
    Generates MIDI patterns for Drums, Bass, and Pads.
    This is a deterministic, rule-based generator.
    """
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)

    def generate_euclidean_pattern(self, pulses: int, steps: int) -> List[int]:
        """
        Generates a Bjorklund (Euclidean) rhythm pattern.
        Returns a list of 1s (hits) and 0s (rests).
        """
        if steps == 0: return []
        if pulses == 0: return [0] * steps
        
        pattern = [[1]] * pulses + [[0]] * (steps - pulses)
        
        while True:
            # Split into lists of same size and remainder
            count = 0
            while count < len(pattern) - 1 and len(pattern[count]) == len(pattern[count+1]):
                count += 1
            count += 1
            
            if count == len(pattern):
                break
                
            remainder = pattern[count:]
            pattern = pattern[:count]
            
            if not remainder:
                break
                
            for i in range(len(remainder)):
                pattern[i % len(pattern)] += remainder[i]
                
        flattened = []
        for p in pattern:
            flattened.extend(p)
        return flattened

    def generate_drum_pattern(self, style: str = "basic", length_bars: int = 4) -> List[MidiNote]:
        """
        Generate a drum pattern.
        """
        notes = []
        # General MIDI Mapping
        KICK = 36
        SNARE = 38
        HAT_CLOSED = 42
        
        for bar in range(length_bars):
            bar_offset = bar * 4.0
            
            if style == "euclidean":
                # Kicks: 5 hits in 16 steps (Tresillo-ish)
                kick_pat = self.generate_euclidean_pattern(5, 16)
                for i, hit in enumerate(kick_pat):
                    if hit:
                        notes.append(MidiNote(KICK, 100, bar_offset + (i * 0.25), 0.1))
                
                # Snares: Standard backbeat
                notes.append(MidiNote(SNARE, 100, bar_offset + 1.0, 0.1))
                notes.append(MidiNote(SNARE, 100, bar_offset + 3.0, 0.1))
                
                # Hats: 13 hits in 16 steps
                hat_pat = self.generate_euclidean_pattern(13, 16)
                for i, hit in enumerate(hat_pat):
                    if hit:
                         notes.append(MidiNote(HAT_CLOSED, 85, bar_offset + (i * 0.25), 0.1))

            elif style == "basic" or style == "rock":
                # Kick on 1 and 3 (with variations)
                notes.append(MidiNote(KICK, 100, bar_offset + 0.0, 0.1))
                if random.random() > 0.5:
                   notes.append(MidiNote(KICK, 90, bar_offset + 2.5, 0.1)) # syncopated kick
                else:
                   notes.append(MidiNote(KICK, 100, bar_offset + 2.0, 0.1))

                # Snare on 2 and 4
                notes.append(MidiNote(SNARE, 100, bar_offset + 1.0, 0.1))
                notes.append(MidiNote(SNARE, 100, bar_offset + 3.0, 0.1))
                
                # Hi-hats 8th notes
                for i in range(8):
                    pos = i * 0.5
                    velocity = 80 + (random.randint(-10, 10)) # humanize
                    if i % 2 == 0: velocity += 10 # accent downbeats
                    notes.append(MidiNote(HAT_CLOSED, velocity, bar_offset + pos, 0.1))
            
            elif style == "four_on_floor":
                # Kick on every beat
                for i in range(4):
                    notes.append(MidiNote(KICK, 110, bar_offset + i, 0.1))
                # Snare on 2 and 4 (optional) or claps
                # Off-beat hats
                for i in range(4):
                    notes.append(MidiNote(HAT_CLOSED, 90, bar_offset + i + 0.5, 0.1))

        return notes

    def get_scale_notes(self, root_note: int, scale_type: str = "major") -> List[int]:
        """
        Returns a list of MIDI notes for one octave of the specified scale.
        """
        intervals = {
            "major": [0, 2, 4, 5, 7, 9, 11],
            "minor": [0, 2, 3, 5, 7, 8, 10],
            "dorian": [0, 2, 3, 5, 7, 9, 10],
            "phrygian": [0, 1, 3, 5, 7, 8, 10],
            "lydian": [0, 2, 4, 6, 7, 9, 11],
            "mixolydian": [0, 2, 4, 5, 7, 9, 10],
            "locrian": [0, 1, 3, 5, 6, 8, 10]
        }
        semitones = intervals.get(scale_type.lower(), intervals["major"])
        return [root_note + s for s in semitones]

    def generate_bass_line(self, chord_progression: List[str], style: str = "root_notes") -> List[MidiNote]:
        """
        Generate a bass line following a chord progression.
        """
        notes = []
        current_time = 0.0
        
        # Simple mapping from chord name to root midi note (octave 1/2)
        # Assuming C Major / A Minor context for MVP simplicity
        root_map = {
            "C": 36, "Dm": 38, "Em": 40, "F": 41, "G": 43, "Am": 45, "Bdim": 47
        }
        
        for chord in chord_progression:
            root = root_map.get(chord, 36) # Default to C
            
            # Determine likely scale context for the chord (simplified)
            # If chord ends in 'm', assume minor/dorian context locally
            chord_scale = "minor" if "m" in chord else "major"
            scale_notes = self.get_scale_notes(root, chord_scale)

            if style == "root_notes":
                # Whole note
                notes.append(MidiNote(root, 100, current_time, 4.0))
            
            elif style == "pumping":
                # 8th notes
                for i in range(8):
                    notes.append(MidiNote(root, 95, current_time + (i*0.5), 0.25))

            elif style == "walking":
                # Quarter notes: Root -> 3rd -> 5th -> 6th/7th
                # Simple walking pattern
                pattern_indices = [0, 2, 4, 5] # Root, 3rd, 5th, 6th
                for i, idx in enumerate(pattern_indices):
                    # Wrap around if index out of bounds (shouldn't happen with 7 note scales)
                    pitch = scale_notes[idx % len(scale_notes)]
                    notes.append(MidiNote(pitch, 90, current_time + i, 0.9))

            elif style == "disco":
                # Octave jumps on offbeats
                # 1 & 2 & 3 & 4 &
                # Root . Root(+12) . Root . Root(+12) .
                for i in range(4):
                    notes.append(MidiNote(root, 100, current_time + i, 0.2))
                    notes.append(MidiNote(root + 12, 90, current_time + i + 0.5, 0.2))

            current_time += 4.0 # Assume 1 bar per chord for now

        return notes

    def generate_pad_chords(self, chord_progression: List[str]) -> List[MidiNote]:
        """
        Generate pad chords.
        """
        notes = []
        current_time = 0.0
        
        # Simple triad offsets
        chord_shapes = {
            "C": [0, 4, 7], "Dm": [0, 3, 7], "Em": [0, 3, 7], 
            "F": [0, 4, 7], "G": [0, 4, 7], "Am": [0, 3, 7]
        }
        root_map_mid = {
            "C": 60, "Dm": 62, "Em": 64, "F": 65, "G": 67, "Am": 69
        }

        for chord in chord_progression:
            root = root_map_mid.get(chord, 60)
            intervals = chord_shapes.get(chord, [0, 4, 7]) # Default Major
            
            for interval in intervals:
                pitch = root + interval
                # Long sustained chord
                notes.append(MidiNote(pitch, 70, current_time, 4.0))
            
            current_time += 4.0

        return notes
    
    def save_to_midi_file(self, notes: List[MidiNote], filename: str):
        """
        Save the list of notes to a standard MIDI file.
        Uses pure python struct packing for MVP or external lib if available.
        For robust output, we'll suggest mido/pretty_midi, but here we can return a list of events
        or rely on REAPER to interpret the JSON data.
        
        Strategy: We will return the data structure, and the REAPER Lua script 
        can potentially reconstruct it, OR we write a .mid file here.
        Writing a .mid file is safer.
        """
        # Placeholder: Real implementation would use `mido` or struct packing.
        # For this MVP, we will assume we pass the NOTE DATA to Reaper via command bridge
        # OR we write a simple MIDI file using a library.
        pass

if __name__ == "__main__":
    gen = MidiGenerator()
    drums = gen.generate_drum_pattern(style="rock")
    # print(drums)

