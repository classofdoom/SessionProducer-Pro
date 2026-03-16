# Author: Tresslers Group

import numpy as np
import librosa
import logging

logger = logging.getLogger(__name__)

class SpectralAnalyzer:
    """
    Advanced spectral analysis for production decision making.
    """
    
    def analyze_spectral_profile(self, y: np.ndarray, sr: int) -> dict:
        """
        Extracts production-relevant spectral features.
        """
        # 1. Spectral Centroid (Overall brightness)
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        brightness = np.mean(centroid)
        
        # 2. Low-Mid Density (200-500Hz) - The "Muck" zone
        stft = np.abs(librosa.stft(y))
        freqs = librosa.fft_frequencies(sr=sr)
        low_mid_mask = (freqs >= 200) & (freqs <= 500)
        low_mid_energy = np.mean(stft[low_mid_mask, :])
        
        # 3. Sibilance Detection (Typical 5kHz - 10kHz for vocals)
        sibilance_mask = (freqs >= 5000) & (freqs <= 10000)
        sibilance_energy = np.mean(stft[sibilance_mask, :])
        
        return {
            "brightness": float(brightness),
            "low_mid_density": float(low_mid_energy),
            "sibilance_level": float(sibilance_energy),
            "spectral_flatness": float(np.mean(librosa.feature.spectral_flatness(y=y)))
        }

    def detect_masking(self, profile_a: dict, profile_b: dict) -> float:
        """
        Simple comparison to detect if profile_b is masking profile_a 
        in the critical low-mid range.
        """
        return profile_b['low_mid_density'] / (profile_a['low_mid_density'] + 1e-6)

