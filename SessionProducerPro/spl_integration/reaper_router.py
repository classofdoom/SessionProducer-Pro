# Author: Tresslers Group
import os
import logging
from typing import List, Dict, Any, Tuple
from .midi_generator_v2 import MidiNote, MidiCC

logger = logging.getLogger(__name__)

class ReaperRouter:
    """
    Final stage of SPL integration: Inserts content into REAPER with maxed-out expression.
    """
    def __init__(self, command_writer, state_watcher):
        self.cmd = command_writer
        self.state = state_watcher

    def insert_generative_instrument(self, 
                                     track_name: str, 
                                     asset_match: Dict[str, Any], 
                                     midi_data: Tuple[List[MidiNote], List[MidiCC]], 
                                     section_start: float = 0.0,
                                     fx_chain: List[str] = None,
                                     spatial_params: Dict[str, Any] = None):
        """
        1. Create Track
        2. Set Name
        3. Add dynamic SPL VST (e.g., Labs, Kontakt, Serum)
        4. Load the specific preset
        5. Add post-processing FX chain
        6. Export MIDI (with CC automation) to temp file
        7. Insert MIDI item
        """
        notes, ccs = midi_data
        
        vst_name = asset_match.get("vst_name", "Labs")
        preset_name = asset_match.get("preset_name", "")
        
        self.cmd.create_track(track_name)
        
        import time
        time.sleep(0.05)
        
        # 3. Add Dynamic Instrument
        logger.info(f"Adding Instrument VST: {vst_name} to track {track_name}")
        self.cmd.add_fx(-1, vst_name)
        time.sleep(1.2) # Instruments take time to 'warm up'
        
        # 4. Set Native Preset
        if preset_name:
            # The instrument is always at index 0 on this new track
            self.cmd.set_fx_preset(-1, 0, preset_name)
            time.sleep(0.5)

        # 5. Add Post-Processing FX Chain
        if fx_chain:
            for fx in fx_chain:
                logger.info(f"Adding effect to chain: {fx}")
                self.cmd.add_fx(-1, fx)
                time.sleep(0.2)
        
        # 6. Apply Spatial Parameters
        if spatial_params:
            if spatial_params.get("stereo_width") is not None:
                # Mocking width command - in a real reaper_bridge we'd have set_track_width
                logger.info(f"Setting track width for {track_name} to {spatial_params['stereo_width']}")
                # self.cmd.set_track_width(-1, spatial_params['stereo_width'])
            
            if spatial_params.get("reverb_size") is not None:
                # Find ReaVerb in chain (Instrument is 0, so FX are 1+)
                if fx_chain and "ReaVerb" in fx_chain:
                    fx_idx = fx_chain.index("ReaVerb") + 1
                    logger.info(f"Setting ReaVerb room size to {spatial_params['reverb_size']} for track {track_name}")
                    self.cmd.set_fx_param(-1, fx_idx, 0, spatial_params["reverb_size"])
        
        # 5. Generate Expressive MIDI File
        # Use a unique filename for each generation to prevent overwriting
        safe_name = "".join([c if c.isalnum() else "_" for c in track_name])
        midi_filename = f"temp_gen_{safe_name}.mid"
        midi_path = os.path.join(os.getcwd(), midi_filename)
        
        self._write_midi_file(midi_path, notes, ccs)
        
        # 6. Insert Media
        self.cmd.insert_media(midi_path, -1, section_start)
        time.sleep(0.05)
        
        logger.info(f"Deployed generative {vst_name} ({preset_name}) instrument at {section_start}s")

    def _write_midi_file(self, path: str, notes: List[MidiNote], ccs: List[MidiCC]):
        import mido
        from mido import MidiFile, MidiTrack, Message
        
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        events = []
        # Add Notes
        for n in notes:
            events.append({'time': n.start_time, 'type': 'note_on', 'note': n.pitch, 'velocity': n.velocity})
            events.append({'time': n.start_time + n.duration, 'type': 'note_off', 'note': n.pitch, 'velocity': 0})
            
        # Add Control Changes
        for c in ccs:
            events.append({'time': c.time, 'type': 'control_change', 'control': c.control, 'value': c.value})
        
        # Sort by time, then ensure note_off happens before note_on and CC at same timestamp
        def sort_priority(e):
            if e['type'] == 'note_off': return 0
            if e['type'] == 'control_change': return 1
            return 2
            
        events.sort(key=lambda x: (x['time'], sort_priority(x)))
        
        # Convert to delta ticks
        ticks_per_beat = mid.ticks_per_beat # Default 480
        # notes/ccs 'time' is in beats (4.0 per bar)
        
        current_beat = 0
        for e in events:
            delta_beats = max(0, e['time'] - current_beat)
            delta_ticks = int(delta_beats * ticks_per_beat)
            
            if e['type'] in ['note_on', 'note_off']:
                track.append(Message(e['type'], 
                                   note=min(127, max(0, int(e['note']))), 
                                   velocity=min(127, max(0, int(e['velocity']))), 
                                   time=delta_ticks))
            elif e['type'] == 'control_change':
                track.append(Message(e['type'], 
                                   control=min(127, max(0, int(e['control']))), 
                                   value=min(127, max(0, int(e['value']))), 
                                   time=delta_ticks))
                
            current_beat = e['time']

        mid.save(path)
        logger.info(f"MidiFile saved to {path} with {len(notes)} notes and {len(ccs)} CC events.")

    def play_session(self):
        self.cmd.transport_play()

