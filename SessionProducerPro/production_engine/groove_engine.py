# Author: Tresslers Group

import random
from typing import List
from .midi_generator import MidiNote

class GrooveEngine:
    """
    Applies humanization and groove to MIDI patterns.
    """

    @staticmethod
    def humanize(notes: List[MidiNote], 
                 timing_jitter: float = 0.005, 
                 velocity_jitter: int = 10,
                 swing: float = 0.0) -> List[MidiNote]:
        """
        Apply random jitter to timing and velocity.
        
        Args:
            notes: List of MidiNote objects.
            timing_jitter: Max beat offset (e.g., 0.01 = 1/100th of a beat).
            velocity_jitter: Max velocity offset.
            swing: Swing factor (0.0 to 1.0). 0.5 is classic MPC swing.
        """
        humanized = []
        for note in notes:
            # 1. Randomized timing jitter
            t_offset = random.uniform(-timing_jitter, timing_jitter)
            
            # 2. Swing (apply to even 16th notes usually)
            # 16th note position = note.start_time * 4
            position_in_beat = note.start_time % 1.0
            
            # Very simple swing: push even 16th/8th notes later
            # Let's say we swing every second 16th note
            sixteenth = 0.25
            if (note.start_time / sixteenth) % 2 >= 0.9: # Simple approximation of "offbeat"
                t_offset += (swing * sixteenth * 0.5)

            new_start = max(0, note.start_time + t_offset)
            
            # 3. Velocity jitter
            v_offset = random.randint(-velocity_jitter, velocity_jitter)
            new_velocity = max(1, min(127, note.velocity + v_offset))
            
            humanized.append(MidiNote(
                pitch=note.pitch,
                velocity=new_velocity,
                start_time=new_start,
                duration=note.duration # Usually we don't jitter duration as much, but could
            ))
            
        return humanized

    @staticmethod
    def apply_quantize(notes: List[MidiNote], grid: float = 0.25) -> List[MidiNote]:
        """
        Snap notes to a grid (e.g., 0.25 for 16th notes).
        """
        quantized = []
        for note in notes:
            new_start = round(note.start_time / grid) * grid
            quantized.append(MidiNote(
                pitch=note.pitch,
                velocity=note.velocity,
                start_time=new_start,
                duration=note.duration
            ))
        return quantized

