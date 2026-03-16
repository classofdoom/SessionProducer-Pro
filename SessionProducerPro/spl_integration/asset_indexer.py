# Author: Tresslers Group
import os
import sqlite3
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SPLAssetIndexer:
    """
    Scans local Spitfire LABS and Splice folders to index available presets and packs.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spl_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pack_name TEXT,
                preset_name TEXT,
                instrument_type TEXT,
                file_path TEXT,
                tags TEXT,
                vst_name TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def scan_directories(self, paths: List[str], file_patterns: List[str] = [".patches", ".nki", ".zpreset", ".zmulti"]):
        """
        Walks through provided paths looking for relevant instrument files.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear old index for a fresh scan
        cursor.execute('DELETE FROM spl_assets')

        patterns = [p.lower() for p in file_patterns]
        found_count = 0
        
        # Load VST name overrides from config if available
        vst_map = {
            ".patches": "Splice INSTRUMENT (Splice)",
            ".nki": "Kontakt",
            ".zpreset": "VSTi: Serum",
            ".zmulti": "VSTi: Serum",
            ".astra": "Splice INSTRUMENT (Splice)",
            ".beatmaker": "Splice INSTRUMENT (Splice)",
            ".vstpreset": "Splice INSTRUMENT (Splice)"
        }
        
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "spl_config.json")
        if os.path.exists(config_path):
            try:
                import json
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    vst_map.update(config_data.get("vst_names", {}))
            except Exception as e:
                logger.warning(f"Could not load VST overrides from config: {e}")

        for path in paths:
            if not os.path.exists(path):
                logger.warning(f"Path does not exist: {path}")
                continue

            logger.info(f"Scanning SPL path: {path}")
            for root, dirs, files in os.walk(path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in patterns:
                        pack_name = os.path.basename(os.path.dirname(root)) # Go up one to get pack name usually
                        if "v0." in pack_name: # Handle versioned folders
                             pack_name = os.path.basename(os.path.dirname(os.path.dirname(root)))
                        
                        preset_name = os.path.splitext(file)[0]
                        
                        # Infer instrument type from name/folder
                        inst_type = self._infer_type(preset_name, pack_name)
                        
                        # 1. Primary Mapping: Extensions (Strongest Signal)
                        vst_name = vst_map.get(ext)
                        
                        # 2. Path-based refine (Contextual Signal)
                        # Specific logic for .vstpreset (which can be either)
                        is_splice_path = "splice" in path.lower() or "splice" in root.lower()
                        is_spitfire_path = "spitfire" in path.lower() or "spitfire" in root.lower() or "labs" in path.lower() or "labs" in root.lower()

                        if ext == ".vstpreset":
                            if is_spitfire_path and not is_splice_path:
                                vst_name = vst_map.get("default_spitfire", "VST3i: LABS (Spitfire Audio)")
                            elif "labs" in file.lower():
                                vst_name = vst_map.get("default_spitfire", "VST3i: LABS (Spitfire Audio)")
                            else:
                                vst_name = vst_map.get("default_splice", "Splice Bridge")
                        
                        # 3. Path prioritization (Only override if not already determined by extension)
                        if not vst_name:
                            if is_splice_path:
                                vst_name = vst_map.get("default_splice", "Splice Bridge")
                            elif is_spitfire_path:
                                vst_name = vst_map.get("default_spitfire", "VST3i: LABS (Spitfire Audio)")
                        
                        # 4. Final safety checks (Correcting mismatched mappings)
                        if is_splice_path and not (".patches" in ext or "labs" in file.lower() or "labs" in root.lower()):
                            # Only force Splice Bridge for things that AREN'T obviously Spitfire
                            vst_name = vst_map.get("default_splice", "Splice Bridge")
                        elif ".patches" in ext or "labs" in file.lower() or "labs" in root.lower():
                            vst_name = vst_map.get(".patches", vst_map.get("default_spitfire", "VST3i: LABS (Spitfire Audio)"))
                            
                        # 4. Final Fallback
                        if not vst_name:
                            if is_splice_path:
                                vst_name = vst_map.get("default_splice", "Splice Bridge")
                            else:
                                vst_name = vst_map.get("default_spitfire", "VST3i: LABS (Spitfire Audio)")
                        
                        # Ensure we don't have None
                        vst_name = vst_name or "Splice Bridge"
                        
                        cursor.execute('''
                            INSERT INTO spl_assets (pack_name, preset_name, instrument_type, file_path, tags, vst_name)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (pack_name, preset_name, inst_type, os.path.join(root, file), "", vst_name))
                        found_count += 1

        conn.commit()
        conn.close()
        logger.info(f"Asset indexing complete. Found {found_count} SPL assets.")

    def _infer_type(self, preset: str, pack: str) -> str:
        name = (preset + " " + pack).lower()
        if any(w in name for w in ["string", "cello", "violin", "viola"]): return "strings"
        if any(w in name for w in ["brass", "trumpet", "horn", "tuba"]): return "brass"
        if any(w in name for w in ["pad", "ambient", "atmosphere", "swell"]): return "pad"
        if any(w in name for w in ["piano", "key", "epiano", "rhodes", "organ", "wurlitzer"]): return "keys"
        if any(w in name for w in ["perc", "drum", "beat", "kit", "kick", "snare", "hat"]): return "percussion"
        if any(w in name for w in ["synth", "lead", "pluck", "osc", "arpeggio"]): return "synth"
        if any(w in name for w in ["guitar", "acoustic", "electric", "bass", "resonator"]): return "pluck"
        if any(w in name for w in ["vocal", "choir", "voice"]): return "pad"
        return "other"

    def query_assets(self, instrument_type: str = None, keyword: str = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM spl_assets WHERE 1=1"
        params = []
        
        if instrument_type:
            if isinstance(instrument_type, list):
                instrument_type = instrument_type[0] if instrument_type else "other"
            query += " AND instrument_type = ?"
            params.append(str(instrument_type))
            
        if keyword:
            if isinstance(keyword, list):
                keyword = " ".join(map(str, keyword))
            query += " AND (preset_name LIKE ? OR pack_name LIKE ?)"
            params.append(f"%{keyword}%")
            params.append(f"%{keyword}%")
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

