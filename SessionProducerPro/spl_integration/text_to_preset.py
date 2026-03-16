# Author: Tresslers Group
import logging
from typing import Dict, Any, List
from .asset_indexer import SPLAssetIndexer

logger = logging.getLogger(__name__)

class TextToPresetMapper:
    """
    Maps user natural language prompts to specific SPL presets and humanization rules.
    """
    def __init__(self, indexer: SPLAssetIndexer, model: str = "gemma2:9b"):
        self.indexer = indexer
        from ai.llm_adapter import LLMAdapter
        self.llm = LLMAdapter(model=model)
        self.used_presets = set() # Track used file paths in the current session

    def reset_session(self):
        """Clears memory of used presets for a new generation run."""
        self.used_presets.clear()
        logger.info("Mapper session memory reset.")

    def map_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parses prompt to find the best matching preset and humanization profile.
        """
        logger.info(f"Mapping prompt to SPL preset: {prompt}")
        
        system_instr = (
            "Extract instrument requirements from prompt. "
            "Categories: [strings, brass, pad, keys, percussion, synth, pluck, other]. "
            "Keywords should be descriptive (e.g., 'heavy orchestral', 'distorted sub', 'analog pulse'). "
            "Moods: [Epic, Cinematic, Suspenseful, Dark, Ethereal, Industrial, Chill, Bright]. "
            "Output JSON:\n"
            "{\n"
            "  \"instrument_type\": \"...\",\n"
            "  \"keyword\": \"...\",\n"
            "  \"vendor\": \"splice | spitfire | labs | kontakt | serum | none\",\n"
            "  \"mood\": \"...\",\n"
            "  \"humanization\": {\"velocity_variation\": 0.1, \"timing_jitter\": 0.01}\n"
            "}"
        )
        
        response = self.llm.generate(f"{system_instr}\n\nPrompt: {prompt}")
        logger.info(f"LLM Mapper Response: {response}")
        
        inst_type = response.get("instrument_type", "other")
        keyword = response.get("keyword", "")
        vendor = str(response.get("vendor", "none")).lower()
        
        logger.info(f"Extracted Vendor: {vendor}")

        # Sanitize list outputs from LLM
        if isinstance(inst_type, list):
            inst_type = inst_type[0] if inst_type else "other"
        if isinstance(keyword, list):
            keyword = ", ".join(keyword) if keyword else ""
        
        # Query indexer for candidates
        # Priority 1: Keyword match (more specific)
        candidates = self.indexer.query_assets(keyword=keyword)
        if not candidates:
            # Priority 2: Type match
            candidates = self.indexer.query_assets(instrument_type=inst_type)
            
        # Filter by vendor if explicitly requested
        if vendor != "none" and candidates:
            vendor_aliases = {
                "spitfire": ["spitfire", "labs"],
                "splice": ["splice"],
                "contact": ["kontakt", "nki"],
                "serum": ["serum", "xfer"]
            }
            targets = vendor_aliases.get(vendor, [vendor])
            
            filtered = [c for c in candidates if any(t in c.get("file_path", "").lower() or t in c.get("vst_name", "").lower() for t in targets)]
            if filtered:
                candidates = filtered
            elif vendor == "splice":
                # ... (virtual asset logic stays same)
                return {
                    "success": True,
                    "match": {
                        "preset_name": f"Splice {keyword or inst_type}",
                        "vst_name": "Splice INSTRUMENT (Splice)",
                        "instrument_type": inst_type,
                        "file_path": "VIRTUAL_SPLICE"
                    },
                    "humanization": response.get("humanization", {}),
                    "mood": response.get("mood", "neutral")
                }
            
        best_match = None
        if candidates:
            import random
            random.shuffle(candidates)
            
            # Secondary Filter: Sub-Instrument Strictness (e.g., Violin should NOT match Cello)
            if keyword:
                sub_instrument_keywords = ["violin", "cello", "viola", "bass", "trumpet", "horn", "trombone", "tuba", "piano", "organ"]
                found_sub = [w for w in sub_instrument_keywords if w in keyword.lower()]
                if found_sub:
                    strict_filtered = [c for c in candidates if any(w in c.get("preset_name", "").lower() or w in c.get("file_path", "").lower() for w in found_sub)]
                    if strict_filtered:
                        candidates = strict_filtered
            
            # Prefer unused ones
            unused = [c for c in candidates if c.get("file_path") not in self.used_presets]
            if unused:
                candidates = unused
            
            best_match = candidates[0]
        
        if best_match and best_match.get("file_path"):
            self.used_presets.add(best_match["file_path"])
        
        return {
            "success": best_match is not None,
            "match": best_match,
            "humanization": response.get("humanization", {}),
            "mood": response.get("mood", "neutral")
        }

