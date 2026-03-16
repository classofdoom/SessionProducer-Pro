# Author: Tresslers Group

import numpy as np
import librosa
import logging

logger = logging.getLogger(__name__)

class HarmonicAnalyzer:
    """
    Analyzes key, scale, and harmonic content of tracks.
    """
    
    def detect_key(self, y: np.ndarray, sr: int) -> dict:
        """
        Detects musical key and scale using chromagram templates.
        """
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_avg = np.mean(chroma, axis=1)
        
        # Key names
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Simple template matching (simplified for MVP)
        major_template = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_template = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        # Circular correlation to find best fit
        def get_best_fit(templates):
            best_val = -1
            best_key = ""
            for i in range(12):
                shifted = np.roll(chroma_avg, -i)
                corr = np.corrcoef(shifted, templates)[0, 1]
                if corr > best_val:
                    best_val = corr
                    best_key = keys[i]
            return best_key, best_val

        major_key, major_score = get_best_fit(major_template)
        minor_key, minor_score = get_best_fit(minor_template)
        
        if major_score > minor_score:
            return {"key": major_key, "scale": "major", "confidence": float(major_score)}
        else:
            return {"key": minor_key, "scale": "minor", "confidence": float(minor_score)}

