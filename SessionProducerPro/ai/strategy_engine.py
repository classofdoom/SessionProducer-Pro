# Author: Tresslers Group

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .intent_classifier import Intent

logger = logging.getLogger(__name__)

@dataclass
class ProductionStrategy:
    intent: Intent
    strategies: List[str] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""
    options: List[Dict[str, Any]] = field(default_factory=list) # For multi-option selection

class StrategyEngine:
    """
    Decides HOW to achieve the classified intent using musical reasoning.
    Now integrates Topology, Masking, and Energy intelligence.
    """
    
    def __init__(self, 
                 model: str = "gemma2:9b", 
                 user_profile=None, 
                 track_personality=None,
                 topology=None,
                 masking=None,
                 energy=None,
                 mastering=None,
                 arrangement_engine=None):
        from .llm_adapter import LLMAdapter
        self.llm = LLMAdapter(model=model)
        self.profile = user_profile
        self.personality = track_personality
        self.topology = topology
        self.masking = masking
        self.energy = energy
        self.mastering = mastering
        self.arrangement = arrangement_engine

    def develop_strategy(self, intent: Intent, project_context: str = "", state_data: Dict[str, Any] = None) -> ProductionStrategy:
        logger.info(f"Developing elite strategy for intent category: {intent.category}")
        
        if intent.category == "general":
            return ProductionStrategy(intent, ["direct_answer"], 1.0, "General query.")

        if intent.category == "troubleshoot":
            return ProductionStrategy(
                intent, 
                ["diagnose_audio", "open_preferences"], 
                1.0, 
                "Initiating system-wide audio diagnostic and opening REAPER device preferences to check driver configuration."
            )

        # Arrangement Logic Hook
        if intent.category == "arrangement" and self.arrangement:
            mood = "dark" if any(w in intent.raw_text.lower() for w in ["dark", "tension", "suspense", "batman"]) else "heroic"
            arr = self.arrangement.generate_cinematic_arrangement(mood=mood, key=intent.parameters.get("key", "C"))
            return ProductionStrategy(
                intent,
                arr.strategies,
                1.0,
                f"Orchestrating a full '{mood}' cinematic structure across {len(arr.sections)} sections."
            )

        # 1. Gather deep context
        topology_summary = self.topology.get_summary() if self.topology else ""
        masking_data = self.masking.detect_conflicts(state_data) if (self.masking and state_data) else []
        energy_data = self.energy.get_correction_strategy(state_data) if (self.energy and state_data) else []
        mastering_advice = self.mastering.suggest_master_chain() if self.mastering else []
        
        pref_str = f"USER PREFERENCES: {self.profile.preferences if self.profile else 'Defaults'}"
        track_memories = ""
        if self.personality:
            for tr in intent.target_tracks:
                track_memories += f"\n{self.personality.get_track_context(tr)}"

        # 2. Build the "Elite Cinematic Conductor & Producer" Prompt
        prompt = (
            "YOU ARE THE WORLD-CLASS CINEMATIC CONDUCTOR & ELITE PRODUCER (Think Hans Zimmer meets Quincy Jones).\n"
            "Your goal is to transform user prompts into high-end, layered, and emotionally resonant musical strategies.\n\n"
            f"PROJECT CONTEXT (REAPER):\n{project_context}\n"
            f"MIX TOPOLOGY:\n{topology_summary}\n"
            f"MASKING CONFLICTS: {masking_data}\n"
            f"ENERGY ANALYSIS: {energy_data}\n"
            f"USER STYLE: {self.profile.preferences if self.profile else 'Cinematic Grade'}\n\n"
            "GENRE ARCHETYPES & DIRECTIVES:\n"
            "1. EPIC/DARK (Batman, Industrial, Ritualistic):\n"
            "   - SCALE: Use 'Phrygian' or 'Locrian' for maximum tension.\n"
            "   - TEXTURE: Use 'pattern': 'pulse' for driving synths/strings.\n"
            "   - HARMONY: Use 'pattern': 'power' (1-5-8 voicings) for low brass/basses.\n"
            "   - DRUMS: Use 'pattern': 'ritualistic' for tribal, heavy tom-focused beats.\n"
            "2. CINEMATIC BEAUTY:\n"
            "   - SCALE: Use 'Lydian' or 'Harmonic Minor'.\n"
            "   - VOICING: Use 'Open Voicings' and 'Voice Leading' (standard).\n"
            "   - FX: Always include 'ReaVerb' with high wetness for strings/pads.\n"
            "3. THE ZIMMER BUILD (Layering & Dynamics):\n"
            "   - Use 'start_bar' calculated from time markers. FORMULA: (Seconds / 60) * (BPM / BeatsPerBar).\n"
            "   - Default to 4 beats per bar. Example: 0:30 at 90 BPM = bar 11.25 (Use 11 or 12).\n"
            "   - Use 'cc_crescendo': true and 'dynamic_curve': 'dramatic' for explosive, high-impact builds.\n\n"
            "ARCHETYPES:\n"
            "- 'Epic Fantasy': Use for Middle-Earth/Witcher vibes. Stagger: Intro (0:00) -> Exploration (0:30) -> Tension (1:20) -> Climax (2:00).\n"
            "- 'Industrial Tension': Use for chugging, darker, modern scores.\n\n"
            "PARAMETERS CONFIG:\n"
            "- 'pattern' options: [melody, chord, arpeggio, pulse, power, ritualistic, lofi, boom_bap]\n"
            "- 'start_bar': Integer (Calculated from user's time markers).\n"
            "- 'cc_crescendo': Boolean for intensity ramps.\n"
            "- 'dynamic_curve': ['linear', 'dramatic'].\n"
            "- 'fx_chain': ALWAYS USE NATIVE NAMES. [ReaEQ, ReaComp, ReaVerb, ReaDelay, Chorus, TubeScreamer].\n"
            "- 'instrument' naming: BE PRECISE. 'Solo Violin (Spitfire)' must map to strings/violin. Avoid generic names if the user is specific.\n\n"
            f"USER INPUT: \"{intent.raw_text}\"\n"
            f"INTENT: {intent.category} - {intent.sub_action}\n\n"
            "DEPLOY MASTER STRATEGY (JSON):\n"
            "   - 'type' MUST BE one of: [melody_generation, chord_generation, drum_generation, texture_generation].\n"
            "{\n"
            "  \"strategies\": [\n"
            "    { \n"
            "      \"type\": \"melody_generation\", \n"
            "      \"parameters\": { \n"
            "        \"instrument\": \"...\", \n"
            "        \"scale\": \"...\", \n"
            "        \"pattern\": \"...\", \n"
            "        \"bars\": 16, \n"
            "        \"start_bar\": 0, \n"
            "        \"cc_crescendo\": true, \n"
            "        \"dynamic_curve\": \"dramatic\", \n"
            "        \"fx_chain\": [\"ReaEQ\", \"ReaComp\", \"ReaVerb\"] \n"
            "      } \n"
            "    }\n"
            "  ],\n"
            "  \"reasoning\": \"A conductor's explanation of the emotional and technical layers.\",\n"
            "  \"confidence\": 0.95,\n"
            "  \"theory_analysis\": \"Detailed harmonic rationale (e.g. 'Using Phrygian b2 for Batman-esque tension').\"\n"
            "}"
        )

        
        response = self.llm.generate(prompt)
        
        if not response or not isinstance(response, dict):
            logger.warning("LLM returned malformed response, using fallback.")
            response = {"strategies": [], "reasoning": "Fallback strategy due to AI timeout or malformed JSON."}

        return ProductionStrategy(
            intent=intent,
            strategies=response.get("strategies", []),
            reasoning=response.get("reasoning", ""),
            confidence=response.get("confidence", 0.0),
            options=response.get("options", [])
        )

