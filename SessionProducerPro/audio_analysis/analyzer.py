# Author: Tresslers Group

import librosa
import numpy as np
import logging
import os
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    """
    Analyzes audio files to extract musical metadata (BPM, Key, Energy).
    """

    @staticmethod
    def analyze(file_path: str) -> Tuple[Optional[float], Optional[str], Optional[float]]:
        """
        Analyze an audio file.
        Returns: (bpm, key, energy_score)
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found for analysis: {file_path}")
            return None, None, None

        try:
            # Load only a portion of the file for speed (e.g., first 30 seconds)
            y, sr = librosa.load(file_path, duration=30)
            
            if len(y) == 0:
                return None, None, None

            # 1. BPM Detection
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)

            # 2. Key Detection (Simplified Chromatogram)
            # Use chromagram to find the most dominant pitch
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            mean_chroma = np.mean(chroma, axis=1)
            
            # Pitches: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
            pitch_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            key_index = np.argmax(mean_chroma)
            
            # Simple major/minor check (very naive: check third)
            # minor third is +3, major third is +4
            is_minor = mean_chroma[(key_index + 3) % 12] > mean_chroma[(key_index + 4) % 12]
            key = pitch_names[key_index] + ("m" if is_minor else "")

            # 3. Energy Score (RMS)
            rms = librosa.feature.rms(y=y)
            energy = float(np.mean(rms))
            # Normalize energy somewhat (naive normalization)
            energy_score = min(1.0, energy * 5.0)

            logger.info(f"Analyzed {os.path.basename(file_path)}: BPM={bpm:.1f}, Key={key}, Energy={energy_score:.2f}")
            return bpm, key, energy_score

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return None, None, None

if __name__ == "__main__":
    # Test stub
    # analyzer = AudioAnalyzer()
    # print(analyzer.analyze("path/to/your/audio.wav"))
    pass

