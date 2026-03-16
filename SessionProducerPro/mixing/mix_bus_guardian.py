# Author: Tresslers Group
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MixBusGuardian:
    """
    Continuously monitors the mix bus for safety and compliance.
    """
    def __init__(self, thresholds: Dict[str, float] = None):
        self.thresholds = thresholds or {
            "max_lufs": -14.0,
            "min_crest_factor": 6.0,
            "max_peak": -1.0
        }

    def check_compliance(self, master_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates the master bus state against target thresholds.
        """
        lufs = master_state.get('lufs', -100.0)
        peak = master_state.get('peak', 0.0)
        crest = master_state.get('crest_factor', 10.0)
        
        issues = []
        if lufs > self.thresholds['max_lufs']:
            issues.append(f"Mix is over-compressed or too loud ({lufs} LUFS).")
            
        if crest < self.thresholds['min_crest_factor']:
            issues.append(f"Low crest factor ({crest:.1f}): Potential loss of transients.")
            
        if peak > self.thresholds['max_peak']:
            issues.append(f"Peak level ({peak:.1f}dB) exceeds safety limit.")
            
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "summary": "Master Bus: Stable" if not issues else f"Master Bus Warnings: {len(issues)}"
        }

