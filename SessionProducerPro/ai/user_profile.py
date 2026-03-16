# Author: Tresslers Group

import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class UserProfile:
    """
    Manages persistent production preferences for the user.
    """
    
    def __init__(self, profile_path: str):
        self.profile_path = profile_path
        self.preferences: Dict[str, Any] = self._load_defaults()
        self.load()

    def _load_defaults(self) -> Dict[str, Any]:
        return {
            "compression_tolerance": 0.5, # 0.0 (subtle) to 1.0 (heavy)
            "vocal_brightness": 0.6,
            "guitar_width": 0.7,
            "mix_density": "moderate",
            "preferred_reverb_type": "plate"
        }

    def load(self):
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read().strip()
                    if content:
                        self.preferences.update(json.loads(content))
                    else:
                        logger.info("Profile file is empty, using defaults.")
            except Exception as e:
                logger.error(f"Failed to load profile: {e}")
                # Don't crash, just use defaults

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")

    def update(self, key: str, value: Any):
        if key in self.preferences:
            self.preferences[key] = value
            self.save()
            logger.info(f"Updated preference: {key} = {value}")

