# Author: Tresslers Group

import os
import sqlite3
import json
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
import hashlib
from audio_analysis.analyzer import AudioAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Asset:
    file_path: str
    filename: str
    file_hash: str
    category: str  # 'loop', 'one_shot', 'midi', 'preset'
    tags: List[str]
    bpm: Optional[float] = None
    key: Optional[str] = None
    length_bars: Optional[float] = None
    energy_score: Optional[float] = None # 0.0 to 1.0

class AssetIndexer:
    def __init__(self, db_path: str = "assets.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                file_hash TEXT,
                category TEXT,
                tags TEXT, -- JSON stored as text
                bpm REAL,
                key TEXT,
                length_bars REAL,
                energy_score REAL,
                last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Index on metadata for faster searching
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bpm ON assets(bpm)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_key ON assets(key)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON assets(category)')
        
        conn.commit()
        conn.close()

    def scan_directory(self, root_path: str, recursive: bool = True):
        """Scan a directory for assets and add them to the database."""
        logger.info(f"Scanning directory: {root_path}")
        
        if not os.path.exists(root_path):
            logger.error(f"Directory not found: {root_path}")
            return

        supported_extensions = {
            '.wav': 'audio', 
            '.aif': 'audio', 
            '.mp3': 'audio', 
            '.mid': 'midi',
            '.fxp': 'preset' 
        }

        count = 0
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for root, dirs, files in os.walk(root_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in supported_extensions:
                    continue

                full_path = os.path.join(root, file)
                
                # Basic metadata extraction (Placeholder for actual analysis logic)
                asset_data = self._analyze_file(full_path, file, ext)
                
                try:
                    self._insert_asset(cursor, asset_data)
                    count += 1
                except sqlite3.IntegrityError:
                     # Asset already exists, could update here if needed
                    pass
            
            if not recursive:
                break
        
        conn.commit()
        conn.close()
        logger.info(f"Scan complete. Indexed {count} new assets.")

    def _analyze_file(self, file_path: str, filename: str, ext: str) -> Asset:
        """
        Analyze a file to extract metadata. 
        Uses AudioAnalyzer for audio files, falls back to heuristics.
        """
        category = 'loop' if 'loop' in filename.lower() else 'one_shot'
        if ext == '.mid':
            category = 'midi'
        
        tags = []
        if 'drum' in filename.lower(): tags.append('drums')
        if 'bass' in filename.lower(): tags.append('bass')
        if 'synth' in filename.lower(): tags.append('synth')
        if 'guitar' in filename.lower(): tags.append('guitar')
        if 'vocal' in filename.lower(): tags.append('vocal')

        bpm = None
        key = None
        energy_score = 0.5

        if ext in ['.wav', '.aif', '.mp3']:
            bpm, key, energy_score = AudioAnalyzer.analyze(file_path)

        # Fallback to filename heuristics if analysis failed
        if bpm is None:
            import re
            bpm_match = re.search(r'(\d{2,3})\s*bpm', filename, re.IGNORECASE)
            if bpm_match:
                try:
                    bpm = float(bpm_match.group(1))
                except ValueError:
                    pass
        
        return Asset(
            file_path=file_path,
            filename=filename,
            file_hash=self._get_file_hash(file_path),
            category=category,
            tags=tags,
            bpm=bpm,
            key=key,
            energy_score=energy_score or 0.5
        )

    def _get_file_hash(self, file_path: str) -> str:
        """Compute SHA256 hash of the file for uniqueness."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                # Read only first 64kb for speed
                buf = f.read(65536)
                hasher.update(buf)
        except Exception:
            return ""
        return hasher.hexdigest()

    def _insert_asset(self, cursor, asset: Asset):
        cursor.execute('''
            INSERT INTO assets (file_path, filename, file_hash, category, tags, bpm, key, length_bars, energy_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            asset.file_path,
            asset.filename,
            asset.file_hash,
            asset.category,
            json.dumps(asset.tags),
            asset.bpm,
            asset.key,
            asset.length_bars,
            asset.energy_score
        ))

if __name__ == "__main__":
    # Test stub
    indexer = AssetIndexer("test_assets.db")
    # indexer.scan_directory("C:/Path/To/Samples")

