# Author: Tresslers Group
from dataclasses import dataclass
from typing import Dict, Any
from .llm_adapter import LLMAdapter
import logging
import sys
import os

# Add parent directory to path to import reaper_bridge
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reaper_bridge.reaper_client import ReaperWebClient

logger = logging.getLogger(__name__)

@dataclass
class Intent:
    action: str
    parameters: Dict[str, Any]
    confidence: float

class ModeRouter:
    """
    Routes natural language queries to specific production modes using an LLM.
    Now equipped with bi-directional REAPER state awareness!
    """
    def __init__(self):
        self.llm = LLMAdapter(model="gemma2:9b") # Optimized for RTX 5070 setup
        self.reaper = ReaperWebClient() # Connects to WebRC automatically
    
    def classify(self, text: str, project_context: str = "") -> Intent:
        """
        Classify user text into an Intent.
        Fetches live REAPER state via WebRC before querying the LLM.
        """
        # Fetch actual live state to enrich context
        live_state = self.reaper.get_project_state()
        state_str = str(live_state)
        
        enriched_context = f"{project_context} | LIVE SESSION STATE: {state_str}"
        logger.info(f"Classifying intent with enriched context: {enriched_context}")
        
        # 1. Rule-based Fast Path 
        text_lower = text.lower()
        if "set tempo" in text_lower or "bpm" in text_lower:
             import re
             m = re.search(r'\d+', text_lower)
             if m:
                 return Intent("set_tempo", {"bpm": int(m.group())}, 1.0)

        # 2. LLM Path
        prompt = (
            f"REAPER CONTEXT: {enriched_context}\n"
            f"User Request: \"{text}\"\n"
            f"Output JSON format: {{ \"action\": \"...\", \"parameters\": {{ ... }}, \"confidence\": 0.9 }}\n"
            f"Available Actions: 'generate_drums', 'generate_bass', 'generate_starter', 'mixing_adjustment', 'structural_change', 'diagnose_audio', 'unknown'."
        )
        
        response = self.llm.generate(prompt)
        
        if "error" in response:
            logger.warning("LLM unavailable, falling back to keywords.")
            return self._fallback_parse(text)
            
        return Intent(
            action=response.get("action", "unknown"),
            parameters=response.get("parameters", {}),
            confidence=response.get("confidence", 0.0)
        )

    def _fallback_parse(self, text: str) -> Intent:
        text = text.lower()
        if "drum" in text:
            style = "basic"
            if "euclidean" in text: style = "euclidean"
            elif "rock" in text: style = "rock"
            elif "four" in text: style = "four_on_floor"
            return Intent("generate_drums", {"style": style}, 0.5)
            
        elif "bass" in text:
            style = "root_notes"
            if "walking" in text: style = "walking"
            elif "disco" in text: style = "disco"
            elif "pumping" in text: style = "pumping"
            return Intent("generate_bass", {"style": style}, 0.5)

        elif "tighten" in text or "mix" in text:
            return Intent("mixing_adjustment", {"type": "tighten_drums"}, 0.8)
            
        elif "vocal" in text and ("pop" in text or "buried" in text):
            return Intent("mixing_adjustment", {"type": "make_vocal_pop"}, 0.8)
            
        elif "swap" in text or "move" in text:
            return Intent("structural_change", {"action": "swap_sections"}, 0.8)
            
        return Intent("unknown", {}, 0.0)

