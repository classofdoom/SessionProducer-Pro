# Author: Tresslers Group

import sqlite3
import json
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AssetMatch:
    file_path: str
    filename: str
    bpm: float
    score: float
    category: str

class AssetMatcher:
    def __init__(self, db_path: str = "assets.db"):
        self.db_path = db_path

    def find_matches(self, 
                     target_bpm: float, 
                     category: str = None, 
                     tags: List[str] = None, 
                     limit: int = 10) -> List[AssetMatch]:
        """
        Find assets matching criteria.
        
        Args:
            target_bpm: The desired BPM.
            category: 'loop', 'one_shot', 'midi', etc.
            tags: List of tags to filter by (e.g. ['drums', 'rock']).
            limit: Max results.
        
        Returns:
            List of AssetMatch objects sorted by relevance.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM assets WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)
        
        # BPM Logic: Strict range for now, roughly +/- 20% is stretchable
        # Ideally, we want exact matches or half/double time.
        # For this MVP, we look for assets within a reasonable stretch range (85% to 115%)
        # But we sort by closeness.
        if target_bpm > 0:
            min_bpm = target_bpm * 0.7
            max_bpm = target_bpm * 1.3
            query += " AND (bpm IS NULL OR (bpm >= ? AND bpm <= ?))"
            params.append(min_bpm)
            params.append(max_bpm)

        # Tag logic (basic textual search for now)
        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f'%"{tag}"%')

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        matches = []
        for row in rows:
            asset_bpm = row['bpm']
            
            # Calculate match score
            score = 1.0
            
            # BPM Penalty
            if asset_bpm:
                # Lower score if BPM is far off
                # Perfect match = 0 distance
                dist = abs(asset_bpm - target_bpm)
                # Normalize distance somewhat
                penalty = (dist / target_bpm) * 0.5
                score -= penalty
            else:
                # If BPM is unknown, slight penalty
                score -= 0.2

            matches.append(AssetMatch(
                file_path=row['file_path'],
                filename=row['filename'],
                bpm=asset_bpm if asset_bpm else 0.0,
                score=max(0.0, score),
                category=row['category']
            ))

        # Sort by score descending
        matches.sort(key=lambda x: x.score, reverse=True)
        
        return matches[:limit]

if __name__ == "__main__":
    # Test stub
    matcher = AssetMatcher("test_assets.db")
    # results = matcher.find_matches(target_bpm=120, tags=['drums'])
    # print(results)

