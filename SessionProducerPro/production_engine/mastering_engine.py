# Author: Tresslers Group
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class MasteringEngine:
    """
    Handles final audio quality, mastering chains, and loudness standards.
    """
    def __init__(self):
        self.standards = {
            "streaming": {"lufs": -14.0, "true_peak": -1.0},
            "club": {"lufs": -9.0, "true_peak": -0.3},
            "cinematic": {"lufs": -23.0, "true_peak": -2.0}
        }

    def suggest_master_chain(self, style: str = "streaming") -> List[Dict[str, Any]]:
        """
        Returns a professional FX chain for the master bus.
        """
        target = self.standards.get(style, self.standards["streaming"])
        
        return [
            {
                "fx_name": "ReaEQ",
                "params": {"LowCut": 20, "HighShelf": 12000, "Gain": 1.2},
                "reasoning": "Subtle air boost and low-end cleanup."
            },
            {
                "fx_name": "ReaComp",
                "params": {"Ratio": 1.5, "Threshold": -24, "Attack": 10, "Release": 100},
                "reasoning": "Transparent glue compression for master cohesion."
            },
            {
                "fx_name": "MasterLimiter",
                "params": {"Ceiling": target["true_peak"], "Threshold": -6.0},
                "reasoning": f"Ensures true peak remains below {target['true_peak']} dB."
            }
        ]

    def get_loudness_advice(self, current_lufs: float, target_style: str = "streaming") -> str:
        target = self.standards.get(target_style, self.standards["streaming"])
        diff = target["lufs"] - current_lufs
        
        if diff > 1.0:
            return f"The track is too quiet ({current_lufs} LUFS). Increase gain by approximately {diff:.1f} dB."
        elif diff < -1.0:
            return f"The track is too hot ({current_lufs} LUFS). Reduce gain to avoid streaming normalization issues."
        return "Loudness is within commercial target range."

