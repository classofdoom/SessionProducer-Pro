# Author: Tresslers Group

import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TrackPersonality:
    """
    Maintains a 'memory' for each track in the project.
    Tracks what processing worked, what was undone, and its role.
    """
    
    def __init__(self):
        self.track_memory: Dict[str, Dict[str, Any]] = {}

    def update_track(self, track_name: str, **kwargs):
        if track_name not in self.track_memory:
            self.track_memory[track_name] = {
                "role": "unknown",
                "history": [],
                "undone_actions": [],
                "preferred_fx": []
            }
            
        for key, value in kwargs.items():
            if key == "history":
                self.track_memory[track_name]["history"].append(value)
            else:
                self.track_memory[track_name][key] = value
                
    def get_track_context(self, track_name: str) -> str:
        memory = self.track_memory.get(track_name, {})
        if not memory:
            return f"No prior memory for {track_name}."
            
        role = memory.get("role", "supporting")
        history = memory.get("history", [])
        last_action = history[-1] if history else "none"
        
        return f"Track '{track_name}' acts as {role}. Last action: {last_action}."

