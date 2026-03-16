# Author: Tresslers Group

from typing import List, Dict, Any
from dataclasses import dataclass, field
import logging

# Use the upgraded MIDI engine
from spl_integration.midi_generator_v2 import MidiGeneratorV2
from spl_integration.theory_engine import TheoryEngine

logger = logging.getLogger(__name__)

@dataclass
class Section:
    name: str 
    length_bars: int
    energy: float # 0.0 to 1.0
    scale: str = "minor"
    pattern: str = "chord"

@dataclass
class Arrangement:
    bpm: float
    key: str
    sections: List[Section]
    strategies: List[Dict[str, Any]] # Collection of ProductionStrategy-like moves

class ArrangementEngine:
    def __init__(self, midi_gen_v2: MidiGeneratorV2 = None):
        self.midi_gen = midi_gen_v2 or MidiGeneratorV2()
        self.theory = TheoryEngine()

    def generate_cinematic_arrangement(self, mood: str = "dark", key: str = "D", bars: int = 32) -> Arrangement:
        """
        Creates a cinematic or genre-specific structure with evolving tension.
        Now includes 'Epic Fantasy' and 'Lofi / Neosoul' archetypes.
        """
        m_lower = mood.lower()
        if "fantasy" in m_lower or "epic" in m_lower:
            structure = [
                Section("Intro (Ancient Darkness)", 8, 0.2, "minor", "pad"),
                Section("Exploration (Ranger)", 16, 0.4, "dorian", "melody"),
                Section("Rising Tension (Orcs)", 16, 0.6, "phrygian", "pulse"),
                Section("Battle Climax (Wraith)", 16, 1.0, "locrian", "power"),
                Section("Dark Resolution (Cost)", 8, 0.3, "minor", "melody")
            ]
        elif "lofi" in m_lower or "chill" in m_lower or "neosoul" in m_lower:
            structure = [
                Section("Intro (Vinyl Haze)", 4, 0.2, "maj_pent", "pad"),
                Section("Groove Entry", 8, 0.4, "dorian", "pulse"),
                Section("Melodic Hook", 16, 0.6, "dorian", "melody"),
                Section("Soul Variation", 16, 0.7, "aeolian", "melody"),
                Section("Faded Outro", 8, 0.3, "maj_pent", "pad")
            ]
        elif "dark" in m_lower or "suspense" in m_lower:
            structure = [
                Section("Tension Crawl", 8, 0.3, "phrygian", "pulse"),
                Section("The Build", 8, 0.6, "phrygian", "power"),
                Section("Climax", 8, 0.9, "harmonic minor", "power"),
                Section("Aftermath", 8, 0.2, "phrygian", "pad")
            ]
        else: # Heroic / Beauty
            structure = [
                Section("Ethereal Intro", 8, 0.2, "lydian", "pad"),
                Section("Rising Theme", 8, 0.5, "lydian", "arpeggio"),
                Section("Heroic Climax", 8, 0.9, "major", "melody"),
                Section("Resolution", 8, 0.3, "lydian", "chord")
            ]

        # Convert structure into actionable strategy blocks for the ExecutionLayer
        strategies = []
        current_bar = 0
        is_lofi = "lofi" in m_lower or "chill" in m_lower or "neosoul" in m_lower
        
        for section in structure:
            # 1. Foundation (Sub/Bed/Pads)
            strategies.append({
                "type": "chord_generation",
                "parameters": {
                    "instrument": "Dusty Lofi Rhodes" if is_lofi else ("Cinematic String Bed" if section.energy < 0.5 else "Low Orchestral Brass"),
                    "scale": f"{key} {section.scale}",
                    "pattern": "pad",
                    "bars": section.length_bars,
                    "start_bar": current_bar,
                    "cc_crescendo": True,
                    "dynamic_curve": "linear" if is_lofi else ("dramatic" if section.energy > 0.8 else "linear"),
                    "stereo_width": 1.2 if is_lofi else 1.0,
                    "reverb_size": 0.8
                }
            })
            
            # 2. Rhythmic Mid-Layer (Pulse/Bass/Ostinato)
            if section.energy > 0.3:
                strategies.append({
                    "type": "melody_generation",
                    "parameters": {
                        "instrument": "Smooth Neosoul Bass" if is_lofi else ("Industrial Percussive Pulse" if section.energy > 0.6 else "Celli Ostinato"),
                        "scale": f"{key} {section.scale}",
                        "pattern": "pulse",
                        "bars": section.length_bars,
                        "start_bar": current_bar,
                        "cc_crescendo": True,
                        "stereo_width": 0.5 if is_lofi else 0.7 # Bass should be mono-ish
                    }
                })

            # 3. High/Melodic Lead (Guitar/Violin)
            if section.energy > 0.4 or "Exploration" in section.name or "Hook" in section.name:
                strategies.append({
                    "type": "melody_generation",
                    "parameters": {
                        "instrument": "Clean Electric Guitar" if is_lofi else ("Haunting Solo Violin" if section.energy < 0.7 else "Epic Heroic Horns"),
                        "scale": f"{key} {section.scale}",
                        "pattern": "melody",
                        "bars": section.length_bars,
                        "start_bar": current_bar,
                        "cc_crescendo": True,
                        "reverb_size": 0.9 if section.energy < 0.5 else 0.6
                    }
                })
                
            # 4. Impact/Percussion Layer
            if section.energy >= 0.4:
                strategies.append({
                    "type": "drum_generation",
                    "parameters": {
                        "instrument": "Dusty Hiphop Kit" if is_lofi else "Taiko Drum Ensemble",
                        "pattern": "boom_bap" if is_lofi else "ritualistic",
                        "bars": section.length_bars,
                        "start_bar": current_bar,
                        "stereo_width": 1.1 if is_lofi else 1.2
                    }
                })
                
            # 5. Texture Layer (Lofi Vinyl / Ambience)
            if is_lofi:
                strategies.append({
                    "type": "texture_generation",
                    "parameters": {
                        "instrument": "Vinyl Crackle & Rain",
                        "bars": section.length_bars,
                        "start_bar": current_bar,
                        "stereo_width": 1.5
                    }
                })
            
            current_bar += section.length_bars

        return Arrangement(
            bpm=85.0 if is_lofi else 120.0,
            key=key,
            sections=structure,
            strategies=strategies
        )

if __name__ == "__main__":
    eng = ArrangementEngine()
    arr = eng.generate_cinematic_arrangement(mood="dark")
    print(f"Generated Cinematic Arrangement: {len(arr.strategies)} layered moves across {len(arr.sections)} sections.")

