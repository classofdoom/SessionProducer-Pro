# Author: Tresslers Group

import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from .llm_adapter import LLMAdapter

logger = logging.getLogger(__name__)

@dataclass
class Intent:
    category: str # mixing, arrangement, energy, spatial, tone, generative, general
    sub_action: str
    target_tracks: List[str]
    parameters: Dict[str, Any]
    confidence: float
    raw_text: str

class IntentClassifier:
    """
    Classifies user natural language into specialized production intents.
    """
    
    def __init__(self, model: str = "gemma2:9b"):
        self.llm = LLMAdapter(model=model)
        
    def classify(self, text: str, project_context: str = "") -> Intent:
        logger.info(f"Classifying intent for: {text}")
        
        prompt = (
            f"REAPER PROJECT CONTEXT:\n{project_context}\n\n"
            f"USER REQUEST: \"{text}\"\n\n"
            "Identify the production intent. Categories:\n"
            "- 'arrangement': Track creation, track naming, setting up sessions, moving items, project structure, tempo/key setup.\n"
            "- 'mixing': Volume, panning, EQ, compression, effects, busing, balancing.\n"
            "- 'generative': Creating MIDI, generating melodies, drum patterns.\n"
            "- 'spatial': Stereo width, reverb, delay, panning.\n"
            "- 'energy': LUFS targets, dynamics, section builds.\n"
            "- 'tone': Timbre changes, distortion, saturation.\n"
            "- 'troubleshoot': Audio issues, 'can't hear anything', driver settings, silence, technical problems.\n"
            "- 'general': Chatting, explaining concepts, or questions that DO NOT require a REAPER action.\n\n"
            "Identify target tracks if mentioned (e.g., 'vocal', 'drums', 'pad', 'track 3'). "
            "If the user mentions specific track numbers, include them exactly as 'track X' in the target_tracks list.\n"
            "Return JSON format:\n"
            "{\n"
            "  \"category\": \"...\",\n"
            "  \"sub_action\": \"...\",\n"
            "  \"target_tracks\": [\"...\"],\n"
            "  \"parameters\": {},\n"
            "  \"confidence\": 0.0\n"
            "}"
        )
        
        response = self.llm.generate(prompt)
        
        if "error" in response:
            return self._fallback_parse(text)
            
        return Intent(
            category=response.get("category", "general"),
            sub_action=response.get("sub_action", "unknown"),
            target_tracks=response.get("target_tracks", []),
            parameters=response.get("parameters", {}),
            confidence=response.get("confidence", 0.0),
            raw_text=text
        )

    def _fallback_parse(self, text: str) -> Intent:
        # Minimal keyword fallback
        t = text.lower()
        cat = "general"
        sub = "unknown"
        targets = []
        
        if "mix" in t or "volume" in t or "pan" in t: cat = "mixing"
        if "drum" in t: targets.append("drums")
        if "vocal" in t: targets.append("vocal")
        if "guitar" in t: targets.append("guitar")
        if "bass" in t: targets.append("bass")
        if "backing" in t: targets.append("backing track")
        if "wider" in t or "stereo" in t: cat = "spatial"
        if "setup" in t or "track" in t: cat = "arrangement"
        if "generate" in t or "add instrument" in t or "add a" in t: cat = "generative"
        if "hear" in t or "sound" in t or "troubleshoot" in t: cat = "troubleshoot"
        
        return Intent(cat, sub, targets, {}, 0.5, text)

