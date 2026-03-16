# Author: Tresslers Group
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class EnergyCurveEngine:
    """
    Ensures musical sections follow professional energy progression.
    """
    def __init__(self):
        self.target_curve = {
            "Intro": 0.25,
            "Verse": 0.40,
            "Pre": 0.60,
            "Chorus": 0.85,
            "Bridge": 0.55,
            "Outro": 0.30
        }

    def analyze_session_energy(self, state: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculates energy metrics for the current session.
        """
        # Mock actual measurement. In production, this pulls from LUFS/RMS in state.json
        return {
            "Verse": state.get('measured_energy_verse', 0.35),
            "Chorus": state.get('measured_energy_chorus', 0.70)
        }

    def get_correction_strategy(self, current_energy: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Identifies underpowered or overcooked sections and suggests moves.
        """
        strategies = []
        for section, target in self.target_curve.items():
            if section in current_energy:
                current = current_energy[section]
                delta = target - current
                
                if abs(delta) > 0.1:
                    logger.info(f"Energy delta detected in {section}: {delta}")
                    strategies.append({
                        "section": section,
                        "delta": delta,
                        "recommendation": self._recommend_move(section, delta)
                    })
        return strategies

    def _recommend_move(self, section: str, delta: float) -> str:
        if delta > 0:
            return f"Increase energy in {section}: Try +1dB on Drum Bus or Parallel Compression."
        else:
            return f"Reduce energy in {section}: Try lowering side elements or reducing bus compression."

