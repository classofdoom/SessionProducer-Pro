# Author: Tresslers Group

import numpy as np
import librosa
import logging

logger = logging.getLogger(__name__)

class DynamicsAnalyzer:
    """
    Measures volume, transients, and dynamic range.
    """
    
    def analyze_dynamics(self, y: np.ndarray) -> dict:
        # RMS Energy
        rms = librosa.feature.rms(y=y)
        avg_rms = np.mean(rms)
        peak = np.max(np.abs(y))
        
        # Crest Factor (Peak to RMS ratio - reveals transient strength)
        crest_factor = peak / (avg_rms + 1e-6)
        
        return {
            "rms_db": float(librosa.amplitude_to_db(np.array([avg_rms]))[0]),
            "peak_db": float(librosa.amplitude_to_db(np.array([peak]))[0]),
            "transient_strength": float(crest_factor)
        }

