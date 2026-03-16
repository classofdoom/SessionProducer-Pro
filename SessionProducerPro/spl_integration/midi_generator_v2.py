# Author: Tresslers Group
import random
import logging
import math
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class MidiNote:
    pitch: int
    velocity: int
    start_time: float
    duration: float

@dataclass
class MidiCC:
    control: int  # CC number (e.g., 1 for Mod Wheel, 11 for Expression)
    value: int    # 0-127
    time: float   # Absolute time in seconds

from .theory_engine import TheoryEngine

class MidiGeneratorV2:
    """
    Generates musical MIDI sequences based on intent, key, and energy.
    Now generates continuous MidiCC data for expressive Spitfire/Orchestral playback.
    """
    def __init__(self):
        self.theory = TheoryEngine()

    def generate_sequence(self, intent_data: Dict[str, Any], energy: float = 0.5) -> Tuple[List[MidiNote], List[MidiCC]]:
        """
        Creates a list of MIDI notes and CC automation for a sequence.
        Returns: (notes, control_changes)
        """
        inst_type = intent_data.get("instrument_type", "pad")
        move_type = intent_data.get("move_type", "")
        # Robustly handle 'key' or 'scale' being None or missing
        key_str = intent_data.get("key") or intent_data.get("scale") or "C major"
        bars = int(intent_data.get("bars", 8))
        
        # Parse key/scale (handles "C major", "A minor", "E", etc.)
        parts = key_str.split()
        root = parts[0] if parts else "C"
        scale_type = parts[1].lower() if len(parts) > 1 else "major"
        
        chords = intent_data.get("chords", [])
        prog = intent_data.get("progression", [])
        
        notes = []
        ccs = []
        
        # Respect the pattern parameter regardless of inferred instrument type
        pattern_type = intent_data.get("pattern")
        
        if "drum" in move_type or "rhythm" in move_type or inst_type == "percussion":
            notes = self._gen_drum_loop(root, scale_type, energy, bars=bars, pattern=pattern_type)
        elif "texture" in move_type:
            # For textures, we just want a long held note or random 'hits'
            notes = self._gen_pad(root, scale_type, energy, bars=bars)
        elif pattern_type == "pulse":
            notes = self._gen_cinematic_pulse(root, scale_type, energy, bars=bars)
        elif pattern_type == "power":
             notes = self._gen_power_chords(chords or prog or [root], energy, bars=bars)
        elif inst_type == "pad" or inst_type == "strings" or inst_type == "brass":
            # ... (rest of old code)
            if pattern_type == "melody":
                notes = self._gen_melody(root, scale_type, energy, bars=bars)
            elif pattern_type == "arpeggio":
                notes = self._gen_arpeggio(root, scale_type, energy, bars=bars)
            elif chords or prog:
                notes = self._gen_from_chords(chords or prog, energy, bars=bars)
            else:
                notes = self._gen_pad(root, scale_type, energy, bars=bars)
            
            # Generate expressive CC data for sustained instruments
            ccs = self._gen_expression_curves(bars, energy)
            
        elif inst_type == "pluck" or inst_type == "keys" or inst_type == "synth":
            if pattern_type == "arpeggio":
                notes = self._gen_arpeggio(root, scale_type, energy, bars=bars)
            elif pattern_type == "melody":
                notes = self._gen_melody(root, scale_type, energy, bars=bars)
            elif chords or prog:
                notes = self._gen_from_chords(chords or prog, energy, bars=bars)
            else:
                notes = self._gen_pluck(root, scale_type, energy, bars=bars)
        else:
            # High energy 'other' (like Guitars) should be plucks/melodies, not pads
            if pattern_type == "melody":
                notes = self._gen_melody(root, scale_type, energy, bars=bars)
            elif pattern_type == "arpeggio":
                notes = self._gen_arpeggio(root, scale_type, energy, bars=bars)
            elif energy > 0.4:
                notes = self._gen_pluck(root, scale_type, energy, bars=bars)
            else:
                notes = self._gen_pad(root, scale_type, energy, bars=bars)
            
        # Apply groove and humanization
        notes = self._apply_groove(notes, energy)
        humanization = intent_data.get("humanization", {})
        notes = self._humanize(notes, humanization)
        
        return notes, ccs

    def _apply_groove(self, notes: List[MidiNote], energy: float) -> List[MidiNote]:
        """
        Adjusts velocity based on rhythmic 'weight' (Downbeats vs Upbeats).
        """
        for n in notes:
            # Check position in the beat (quantized to 16th notes)
            position_in_bar = n.start_time % 4.0
            is_downbeat = (position_in_bar % 1.0) < 0.05
            is_offbeat = abs((position_in_bar % 0.5) - 0.25) < 0.05
            
            if is_downbeat:
                n.velocity = int(n.velocity * 1.1)
            elif is_offbeat:
                n.velocity = int(n.velocity * 0.85)
                
            # Random velocity accents based on energy
            if random.random() < (energy * 0.2):
                n.velocity = min(127, int(n.velocity * 1.15))
                
        return notes

    def _gen_expression_curves(self, bars: int, energy: float) -> List[MidiCC]:
        """
        Generates expressive curves with 'Organic Jitter' to avoid mechanical perfection.
        """
        ccs = []
        bar_len = 4.0
        total_time = bars * bar_len
        steps = int(total_time / 0.1)
        
        base_val = int(30 + (energy * 40))
        swell_depth = int(30 + (energy * 20))
        swell_freq = math.pi / (bar_len * 2)
        
        for i in range(steps):
            t = i * 0.1
            # Organic Chaos: Subtle random variation
            chaos = random.uniform(-5, 5) * energy
            
            # Mod Wheel (CC1)
            swell = math.sin(t * swell_freq) 
            cc1_val = max(0, min(127, int(base_val + (swell * swell_depth) + chaos)))
            
            # Expression (CC11) - slightly offset
            swell11 = math.sin((t - 0.5) * swell_freq)
            base11_val = 60 + int(energy * 30)
            cc11_val = max(0, min(127, int(base11_val + (swell11 * 40) + chaos)))
            
            ccs.append(MidiCC(control=1, value=cc1_val, time=t))
            ccs.append(MidiCC(control=11, value=cc11_val, time=t))
            
        return ccs

    def _gen_from_chords(self, chord_list: List[str], energy: float, bars: int = 4) -> List[MidiNote]:
        """
        Generates MIDI notes with Voice Leading, Rhythmic Displacement, and Open Voicings.
        """
        if not chord_list:
            return []

        notes = []
        bar_len = 4.0
        prev_chord = []
        
        total_bar_count = 0
        while total_bar_count < bars:
            for chord_str in chord_list:
                if total_bar_count >= bars: break
                
                import re
                match = re.match(r"([A-Ga-g][#b]?)(.*)", chord_str)
                if not match: continue
                
                chord_root, chord_suffix = match.groups()
                chord_type = "min7" if "m" in chord_suffix else "maj7"
                if "7" not in chord_suffix and chord_suffix != "m": 
                    chord_type = "min" if "m" in chord_suffix else "maj"

                chord_notes = self.theory.get_voice_led_chord(chord_root, chord_type, prev_notes=prev_chord)
                prev_chord = chord_notes
                
                # Displacement: 'Push' the chords slightly based on energy
                displacement = random.choice([-0.25, 0.0, 0.0]) if energy > 0.4 else 0.0
                start_time = (total_bar_count * bar_len) + displacement
                
                # Open Voicing: drop middle note
                final_notes = list(chord_notes)
                if len(final_notes) >= 3 and random.random() < 0.4:
                    final_notes[1] -= 12
                
                strum_delay = random.uniform(0.01, 0.03)
                for j, pitch in enumerate(sorted(final_notes)):
                    notes.append(MidiNote(
                        pitch=pitch,
                        velocity=int(50 + (energy * 30)),
                        start_time=max(0, start_time + (j * strum_delay)),
                        duration=bar_len - 0.2
                    ))
                total_bar_count += 1
        return notes

    def _gen_arpeggio(self, root: str, scale_type: str, energy: float, bars: int = 4) -> List[MidiNote]:
        """
        Generates complex rhythmic arpeggio patterns with varying densities.
        """
        notes = []
        bar_len = 4.0
        step_len = 0.25 # 16th notes
        
        scale = self.theory.get_scale_notes(root, scale_type, octaves=2, start_octave=3)
        arp_notes = [scale[0], scale[2], scale[4], scale[7], scale[9]] # 1-3-5-8-10
        
        patterns = [
            [0, 1, 2, 3, 4], # Up
            [4, 3, 2, 1, 0], # Down
            [0, 2, 1, 3, 4, 3, 2, 0], # Back and forth
            [0, 4, 2, 3, 1]  # Wide/Interleaved
        ]
        active_pattern = random.choice(patterns)
        
        for b in range(bars):
            # Syncopation: Varied rhythms based on energy
            for i in range(16):
                prob = 0.5 + (energy * 0.4)
                if i % 4 != 0: prob -= 0.3 # Ghost notes/weaker offbeats
                
                if random.random() < prob:
                    idx = active_pattern[i % len(active_pattern)]
                    pitch = arp_notes[idx % len(arp_notes)]
                    
                    # Vary duration: staccato vs legato
                    duration = 0.15 if random.random() < 0.7 else 0.4
                    
                    notes.append(MidiNote(
                        pitch=pitch,
                        velocity=int(60 + (energy * 30)),
                        start_time=(b * bar_len) + (i * step_len),
                        duration=duration
                    ))
        return notes

    def _gen_pluck(self, root: str, scale_type: str, energy: float, bars: int = 4) -> List[MidiNote]:
        """
        Generates short, rhythmic 'pluck' patterns. 
        Ideal for guitars, synths, and keys in chill/lofi settings.
        """
        notes = []
        bar_len = 4.0
        step_len = 0.25 # 16th notes
        scale = self.theory.get_scale_notes(root, scale_type, octaves=1, start_octave=4)
        
        # Define a few rhythmic templates for plucks
        rhythms = [
            [0, 1.5, 2.5, 3.5], # Syncopated
            [0, 0.5, 1.0, 2.0, 2.5], # Driving
            [0.75, 1.75, 2.75, 3.75], # Off-beats
            [0, 2.0, 2.5] # Simple
        ]
        
        for b in range(bars):
            active_rhythm = random.choice(rhythms)
            for start in active_rhythm:
                # 16th note jitter for 'human' feel even before the humanize pass
                jitter = random.uniform(-0.02, 0.02)
                
                # Pick a random scale tone, favoring the root/third
                pitch = random.choice(scale)
                if start % 1.0 == 0 and random.random() < 0.6:
                    pitch = scale[0] # Root on downbeats
                
                notes.append(MidiNote(
                    pitch=pitch,
                    velocity=int(60 + (energy * 30)),
                    start_time=(b * bar_len) + start + jitter,
                    duration=0.15 # Short and plucky
                ))
        return notes

    def _gen_melody(self, root: str, scale_type: str, energy: float, bars: int = 4) -> List[MidiNote]:
        """
        Generates an evolving structural melody using Phrased Evolution.
        Motifs transform every 4 bars to prevent 'mechanical' repetition.
        """
        notes = []
        bar_len = 4.0
        scale = self.theory.get_scale_notes(root, scale_type, octaves=2, start_octave=5)
        chord_tones = [scale[0], scale[2], scale[4], scale[7]]
        
        # 1. Define Phrasing Templates (transformed every 4 bars)
        def gen_evolving_motif(comp, bar_idx):
            motif_rhythm = []
            for i in range(16):
                prob = 0.2 + (comp * 0.4)
                if i % 4 == 0: prob += 0.3 # Strong beats
                # Evolving variation: change probabilities based on bar_idx
                if bar_idx % 4 >= 2: prob += 0.1 
                if random.random() < prob:
                    motif_rhythm.append(i * 0.25)
            # TRANSFORM: Every 4 bars, pick a new core pitch sequence
            pitch_template = [random.choice(scale) for _ in range(len(motif_rhythm))]
            return motif_rhythm, pitch_template

        for b in range(bars):
            # Every 4 bars, 'evolve' the motif
            if b % 4 == 0:
                q_rhythm, q_pitches = gen_evolving_motif(energy, b)
                a_rhythm, a_pitches = gen_evolving_motif(energy + 0.1, b)

            is_response = (b % 2 == 1)
            rhythm = a_rhythm if is_response else q_rhythm
            pitches = a_pitches if is_response else q_pitches
            
            # 2. MELODIC BREATHING: Skip random phrases to let the music 'breathe'
            if random.random() < 0.15: continue 

            for i, start in enumerate(rhythm):
                # Structural Logic: Favor chord tones on strong beats
                is_strong = (start % 2.0 == 0)
                pitch = pitches[i]
                
                if not is_response and is_strong and random.random() < 0.7:
                    pitch = random.choice(chord_tones)
                
                # TRANSFORM: Simple melodic inversion on the 'Response'
                if is_response and random.random() < 0.3:
                    pitch = scale[(scale.index(pitch) + 2) % len(scale)]
                
                # Vary duration: short 'stabs' vs long 'expressive' notes
                duration = 0.2
                if start % 1.0 == 0 and random.random() < 0.5:
                    duration = 0.8
                
                # Velocity Gradient: Melodic notes shouldn't all be the same volume
                vel = int(65 + (energy * 40))
                if is_strong: vel += 15
                
                notes.append(MidiNote(
                    pitch=pitch,
                    velocity=min(127, vel),
                    start_time=(b * bar_len) + start,
                    duration=duration
                ))
        return notes

    def _gen_pad(self, root: str, scale_type: str, energy: float, bars: int = 4) -> List[MidiNote]:
        """
        Generates lush, voice-led pad progressions.
        """
        diatonic = self.theory.get_diatonic_chords(root, scale_type)
        if not diatonic:
            progression = [{"degree": "I", "type": "maj7"}, {"degree": "IV", "type": "maj7"}]
        else:
            # Pick a common progression: I - IV - vi - V
            prog_degrees = [0, 3, 5, 4] if len(diatonic) >= 6 else [0, 3]
            progression = [diatonic[i] for i in prog_degrees]

        notes = []
        bar_len = 4.0
        prev_chord = []
        
        for i in range(bars):
            chord_info = progression[i % len(progression)]
            
            # Use voice leading for the pads
            chord_notes = self.theory.get_voice_led_chord(root, chord_info["type"], prev_chord)
            prev_chord = chord_notes
            
            # Spread out the pad notes (Open Voicing)
            for j, pitch in enumerate(chord_notes):
                # Shift some notes down an octave for depth
                final_pitch = pitch
                if j == 0: final_pitch -= 12 # Root bass note
                
                notes.append(MidiNote(
                    pitch=final_pitch,
                    velocity=int(45 + (energy * 25)),
                    start_time=(i * bar_len),
                    duration=bar_len - 0.05
                ))
        return notes

    def _gen_power_chords(self, chord_list: List[str], energy: float, bars: int = 4) -> List[MidiNote]:
        """
        Generates heavy 1-5-8 'Power Chords' for brass, low strings, or synths.
        """
        notes = []
        bar_len = 4.0
        total_bar_count = 0
        while total_bar_count < bars:
            for chord_str in chord_list:
                if total_bar_count >= bars: break
                import re
                match = re.match(r"([A-Ga-g][#b]?)", chord_str)
                if not match: continue
                root_note = self.theory.get_chord_notes(match.group(1), "power", octave=int(2 + (energy * 2)))
                for pitch in root_note:
                    notes.append(MidiNote(pitch=pitch, velocity=int(80 + (energy * 40)), start_time=(total_bar_count * bar_len), duration=bar_len - 0.1))
                total_bar_count += 1
        return notes

    def _gen_cinematic_pulse(self, root: str, scale_type: str, energy: float, bars: int = 4) -> List[MidiNote]:
        """
        Generates a driving 8th or 16th note 'pulse' on the root or pedal note.
        Classic Zimmer tension builder.
        """
        notes = []
        bar_len = 4.0
        # 8th note pulses (0.5) or 16th notes (0.25)
        step = 0.5 if energy < 0.7 else 0.25
        root_pitch = self.theory.get_scale_notes(root, scale_type, octaves=1, start_octave=2)[0]
        
        for b in range(bars):
            for i in range(int(bar_len / step)):
                # Subtle velocity variation for 'chugging' feel
                vel = int(70 + (energy * 40))
                if i % 4 != 0: vel = int(vel * 0.8) # Accent every quarter note
                
                notes.append(MidiNote(
                    pitch=root_pitch,
                    velocity=vel,
                    start_time=(b * bar_len) + (i * step),
                    duration=step * 0.8 # Short and driving
                ))
        return notes

    def _gen_drum_loop(self, root: str, scale_type: str, energy: float, bars: int = 4, pattern: str = None) -> List[MidiNote]:
        """
        Generates standard MIDI drum patterns with Dynamic Fills every 8 bars.
        """
        notes = []
        bar_len = 4.0
        step_len = 0.25
        
        patterns = {
            "lofi": {
                "kick": [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                "hat": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] 
            },
            "boom_bap": {
                "kick": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
                "hat": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            },
            "ritualistic": {
                "kick": [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
                "snare": [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                "hat": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                "tom": [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0]
            }
        }
        
        p_key = pattern if pattern in patterns else ("lofi" if energy < 0.6 else "boom_bap")
        active = patterns[p_key]
        
        for b in range(bars):
            # Dynamic Fill Logic: Every 8 bars (or last bar), add a flourish
            is_fill_bar = (b % 8 == 7) or (b == bars - 1 and bars > 1)
            
            for i in range(16):
                time_offset = (b * bar_len) + (i * step_len)
                
                # Standard Pattern
                if not is_fill_bar or i < 12:
                    if active["kick"][i]:
                        notes.append(MidiNote(36, int(95 + energy * 20), time_offset, 0.15))
                    if active["snare"][i]:
                        notes.append(MidiNote(38, int(90 + energy * 25), time_offset, 0.15))
                    if active["hat"][i]:
                        vel = int(65 + energy * 20) if i % 2 == 0 else int(45 + energy * 15)
                        notes.append(MidiNote(42, vel, time_offset, 0.1))
                    if "tom" in active and active["tom"][i]:
                        pitch = random.choice([41, 43, 45])
                        notes.append(MidiNote(pitch, int(85 + energy * 30), time_offset, 0.15))
                else:
                    # THE FILL: Rapid Snare/Tom rolls at end of phrase
                    prob = 0.4 + (energy * 0.4)
                    if random.random() < prob:
                        pitch = 38 if random.random() < 0.6 else random.choice([41, 43, 45])
                        notes.append(MidiNote(pitch, int(100 + energy * 27), time_offset, 0.1))
                    
        return notes

    def _humanize(self, notes: List[MidiNote], params: Dict[str, Any]) -> List[MidiNote]:
        v_var = params.get("velocity_variation", 0.08)
        t_jit = params.get("timing_jitter", 0.008)
        
        for n in notes:
            n.velocity = int(n.velocity * (1 + random.uniform(-v_var, v_var)))
            n.start_time += random.uniform(-t_jit, t_jit)
        return notes


