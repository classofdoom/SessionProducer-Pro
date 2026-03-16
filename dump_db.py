# Author: Tresslers Group
import sqlite3
import os

db_path = "SessionProducerPro/spl_assets.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("--- FIRST 5 SPLICE ASSETS ---")
    cursor.execute("SELECT * FROM spl_assets WHERE file_path LIKE '%splice%' LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(dict(row))
        
    print("\n--- FIRST 5 SPITFIRE ASSETS ---")
    cursor.execute("SELECT * FROM spl_assets WHERE file_path NOT LIKE '%splice%' LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(dict(row))
        
    conn.close()
else:
    print(f"Database not found at {db_path}")

