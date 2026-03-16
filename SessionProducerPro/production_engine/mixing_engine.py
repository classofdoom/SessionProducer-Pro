# Author: Tresslers Group
import logging
from .production_rules import ProductionRules
from reaper_bridge.command_writer import CommandWriter

logger = logging.getLogger(__name__)

class MixingEngine:
    """
    Handles higher-level mixing commands and applies FX chains.
    """
    
    def __init__(self, command_writer: CommandWriter):
        self.cmd = command_writer

    def tighten_drums(self, track_index: int):
        """Apply compression and EQ to tighten drums."""
        logger.info(f"Tightening drums on track {track_index}")
        self.cmd.add_fx(track_index, "ReaComp")
        self.cmd.add_fx(track_index, "ReaEQ")
        # In a real app, we'd send specific parameter settings via OSC or Chunking
        
    def make_vocal_pop(self, vocal_track_index: int, backing_bus_index: int):
        """Carve space for vocals in the backing tracks."""
        logger.info(f"Applying 'Pop' processing to vocal track {vocal_track_index}")
        # 1. Subtle compression on vocal
        self.cmd.add_fx(vocal_track_index, "ReaComp")
        # 2. Ducking of backing tracks? Or EQ carved.
        # Simple ducking for MVP
        self.cmd.duck_track(backing_bus_index, -3.0)
        
    def widen_guitars(self, track_indices: list):
        """Apply panning and stereo width."""
        if len(track_indices) >= 2:
            self.cmd.set_pan(track_indices[0], -0.8) # Hard left
            self.cmd.set_pan(track_indices[1], 0.8)  # Hard right

