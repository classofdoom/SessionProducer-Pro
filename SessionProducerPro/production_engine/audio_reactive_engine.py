# Author: Tresslers Group

import logging
from audio_analysis.analyzer import AudioAnalyzer
from reaper_bridge.command_writer import CommandWriter

logger = logging.getLogger(__name__)

class AudioReactiveEngine:
    """
    Analyzes user tracks and makes mixing/arrangement decisions.
    """
    
    def __init__(self, command_writer: CommandWriter):
        self.cmd = command_writer
        self.analyzer = AudioAnalyzer()

    def process_vocal_track(self, vocal_file_path: str, vocal_track_index: int, backing_bus_index: int):
        """
        Analyze vocal and adjust backing accordingly.
        """
        logger.info(f"Reactive processing for vocal: {vocal_file_path}")
        bpm, key, energy = self.analyzer.analyze(vocal_file_path)
        
        if energy and energy > 0.02: # If there is actual content
            # 1. Duck the backing more if the vocal is high energy
            duck_amount = -3.0 - (energy * 10.0) # Base -3dB, up to -13dB
            self.cmd.duck_track(backing_bus_index, duck_amount)
            
            # 2. Could also suggest key changes or tempo matches if they differ
            logger.info(f"Vocal energy is {energy:.2f}. Applied {duck_amount:.1f}dB ducking.")
            
    def suggest_arrangement_for_audio(self, audio_file_path: str):
        """
        Analyze an audio file and return a suggested arrangement structure.
        (e.g., detecting verse/chorus based on energy changes)
        """
        # This would require full file RMS analysis vs just the first 30s
        # For MVP, we point out where the energy is high
        pass

