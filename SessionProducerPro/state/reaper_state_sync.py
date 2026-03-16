# Author: Tresslers Group

import json
import os
import time
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ReaperStateWatcher:
    """
    Watches state.json written by REAPER to keep the application in sync.
    Now expanded with a 'Live Session Map' for AI Context injection.
    """
    
    def __init__(self, state_file_path: str):
        self.state_file = state_file_path
        self.current_state: Dict[str, Any] = {}
        self.last_mtime = 0
        
    def poll(self) -> Optional[Dict[str, Any]]:
        """Check if state file has updated and parse it."""
        if not os.path.exists(self.state_file):
            return None
            
        try:
            mtime = os.path.getmtime(self.state_file)
            if mtime > self.last_mtime:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.current_state = data
                    self.last_mtime = mtime
                    return data
        except Exception as e:
            logger.debug(f"Error polling Reaper state: {e}")
            
        return None

    def get_track_info(self, name_or_idx: Any) -> Optional[Dict[str, Any]]:
        tracks = self.current_state.get('tracks', [])
        for i, tr in enumerate(tracks):
            if isinstance(name_or_idx, int) and i == name_or_idx:
                return tr
            if isinstance(name_or_idx, str) and tr['name'].lower() == name_or_idx.lower():
                tr['index'] = i # Inject index for convenience
                return tr
        return None

    def get_context_summary(self) -> str:
        """
        Returns a rich string description of the project for the AI.
        Fulfills 'Live Session Map' requirement in Path A.
        """
        if not self.current_state:
            return "REAPER Session is currently offline or uninitialized."
            
        bpm = self.current_state.get('bpm', 120)
        tracks = self.current_state.get('tracks', [])
        transport = self.current_state.get('transport_status', 'stopped')
        pos = self.current_state.get('cursor_pos', 0.0)
        
        details = []
        for i, tr in enumerate(tracks):
            fx_list = tr.get('fx', [])
            fx_str = f" [FX: {', '.join(fx_list)}]" if fx_list else ""
            rec_str = " (RECORD ARMED)" if tr.get('record_armed') else ""
            details.append(f"Track {i+1}: {tr['name']}{fx_str}{rec_str}")
            
        summary = (
            f"--- REAPER LIVE SESSION MAP ---\n"
            f"Transport: {transport.capitalize()} | Playhead: {pos:.2f}s | Tempo: {bpm} BPM\n"
            f"Active Tracks ({len(tracks)}):\n" + "\n".join(details) + "\n"
            f"--- END MAP ---"
        )
        return summary

