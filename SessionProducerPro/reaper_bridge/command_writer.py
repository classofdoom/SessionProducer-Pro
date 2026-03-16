# Author: Tresslers Group
import json
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the new WebRC client
from .reaper_client import ReaperWebClient

class CommandWriter:
    """
    Maxed-Out version!
    Sends commands instantly to REAPER via WebRC SetExtState.
    No file I/O locks. No spin waits. 100x faster than disk polling.
    OSC is replaced entirely by native ExtState parsing in lua.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.reaper = ReaperWebClient(host=host, port=port)
        logger.info(f"CommandWriter initialized via WebRC on {host}:{port}")

    def send_command(self, action: str, params: dict = None):
        """
        Sends a JSON payload instantly to REAPER's ExtState.
        """
        if params is None:
            params = {}
            
        payload = {
            "action": action,
            **params
        }
        
        try:
            json_str = json.dumps(payload)
            # The client's _send_request now handles safe quoting of this path
            endpoint = f"SET/EXTSTATE/SessionProducer/Command/{json_str}"
            self.reaper._send_request(endpoint)
            logger.info(f"Sent instant command via ExtState: {action} {params}")
        except Exception as e:
            logger.error(f"Failed to send ExtState command: {e}")

    def create_track(self, name: str = "New Track"):
        self.send_command("insert_track", {"name": name})

    def set_tempo(self, bpm: int):
        self.send_command("set_tempo", {"bpm": bpm})
    
    def delete_track_by_index(self, track_index: int):
        self.send_command("delete_track", {"track_index": track_index})
    
    def insert_media(self, file_path: str, track_index: int = 0, position: float = 0.0):
        self.send_command("insert_media", {
            "path": file_path.replace("\\", "/"), 
            "track_index": track_index,
            "position": position
        })

    def add_fx(self, track_index: int, fx_name: str):
        self.send_command("add_fx", {"track_index": track_index, "fx_name": fx_name})

    def set_fx_preset(self, track_index: int, fx_index: int, preset_name: str):
        self.send_command("set_fx_preset", {
            "track_index": track_index,
            "fx_index": fx_index,
            "preset_name": preset_name
        })

    def set_pan(self, track_index: int, pan: float):
        self.send_command("set_pan", {"track_index": track_index, "pan": pan})

    def set_volume(self, track_index: int, volume_db: float):
        self.send_command("set_volume", {"track_index": track_index, "volume_db": volume_db})

    def ramp_volume(self, track_index: int, start_db: float, end_db: float, duration: float = 0.5):
        """
        Delegates the heavy lifting of smooth automation to the REAPER GUI thread!
        """
        self.send_command("ramp_volume", {
            "track_index": track_index,
            "start_db": start_db,
            "end_db": end_db,
            "duration": duration
        })
            
    def duck_track(self, track_index: int, db: float = -6.0):
        self.ramp_volume(track_index, 0.0, db, duration=0.2)

    def transport_play(self):
        self.send_command("transport_play")

    def transport_stop(self):
        self.send_command("transport_stop")

    def diagnose_audio(self):
        # Now handled cleanly by reaper_client.py's native diagnose_audio
        print(self.reaper.diagnose_audio())

    def open_preferences(self):
        self.send_command("open_preferences")

if __name__ == "__main__":
    writer = CommandWriter()

