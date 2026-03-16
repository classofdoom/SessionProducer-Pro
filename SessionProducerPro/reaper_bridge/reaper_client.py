# Author: Tresslers Group
import urllib.request
import urllib.parse
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ReaperWebClient:
    """
    Bi-directional communication client for the REAPER Web Interface (WebRC).
    This completely replaces the fragile JSON file polling mechanism.
    
    Users must enable the Web Interface in REAPER:
    Preferences -> Control/OSC/Web -> Add -> Web browser interface.
    Set Port to 8080 (default).
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.base_url = f"http://{host}:{port}/_"
        
    def _send_request(self, command: str) -> Optional[str]:
        """Send an HTTP GET request to the REAPER Web API."""
        # CRITICAL: We must preserve slashes for the API routing, but quote spaces/special chars
        url = f"{self.base_url}/{urllib.parse.quote(command, safe='/')}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=2.0) as response:
                return response.read().decode('utf-8')
        except urllib.error.URLError as e:
            logger.error(f"Failed to connect to REAPER Web Interface at {self.base_url}. Ensure it is enabled in Preferences. Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error executing REAPER command '{command}': {e}")
            return None

    def execute_action(self, action_id: str):
        """Execute a REAPER action by its Command ID (e.g., 40016 for Preferences)."""
        self._send_request(str(action_id))

    def get_project_state(self) -> Dict[str, Any]:
        """
        Fetches the complete state of the REAPER project.
        This provides the AI with "eyes" into the session.
        """
        # The /_/TRACK command in REAPER WebRC returns a block of text separated by newlines
        # Format usually: 
        # TRACK \t id \t name \t flags \t volume \t pan \t mute \t solo \t ...
        response = self._send_request("TRACK")
        if not response:
            return {"error": "Could not connect to REAPER"}
            
        lines = response.strip().split('\n')
        tracks = []
        master = {}
        
        for line in lines:
            parts = line.split('\t')
            if not parts:
                continue
                
            line_type = parts[0]
            if line_type == "TRACK" and len(parts) >= 8:
                # Basic parsing based on REAPER WebRC docs
                flags = int(parts[3])
                track_info = {
                    "id": parts[1],
                    "name": parts[2],
                    "volume_db": float(parts[4]), # Usually returned as a ratio, but we normalize it in the router
                    "pan": float(parts[5]),
                    "is_muted": (flags & 1) != 0,
                    "is_soloed": (flags & 2) != 0,
                }
                
                if parts[1] == "0":
                    master = track_info
                else:
                    tracks.append(track_info)
                    
        return {
            "master_track": master,
            "tracks": tracks,
            "transport_state": "unknown" 
        }

    def get_bpm(self) -> float:
        """Fetches the current project BPM from REAPER."""
        response = self._send_request("TRANSPORT")
        if response:
            parts = response.split('\t')
            if len(parts) >= 2:
                try:
                    val = float(parts[2]) # Wait, parts[0]=TRANSPORT, parts[1]=Status, parts[2]=BPM
                    if val > 10.0:
                        return val
                except (ValueError, IndexError):
                    pass
        return 120.0

    def diagnose_audio(self) -> Dict[str, Any]:
        """
        AI Audio Troubleshooting Command:
        Diagnoses why the user might not be hearing audio by inspecting the project state.
        """
        state = self.get_project_state()
        if "error" in state:
            return {"diagnosis": ["CONNECTION_FAILED"], "details": "Cannot connect to REAPER Web API."}
            
        issues = []
        details = []
        
        # 1. Check Master Output
        master = state.get("master_track", {})
        if master.get("is_muted"):
            issues.append("MASTER_MUTED")
            details.append("The Master Track is muted, blocking all audio output.")
            
        # 2. Check if tracks are soloed (muting others)
        soloed_tracks = [t for t in state.get("tracks", []) if t.get("is_soloed")]
        if soloed_tracks:
            issues.append("TRACKS_SOLOED")
            names = ", ".join(t["name"] for t in soloed_tracks)
            details.append(f"The following tracks are soloed, muting everything else: {names}")
            
        # 3. Check for specific muted tracks
        muted_tracks = [t for t in state.get("tracks", []) if t.get("is_muted")]
        if muted_tracks:
            issues.append("TRACKS_MUTED")
            names = ", ".join(t["name"] for t in muted_tracks)
            details.append(f"These individual tracks are muted: {names}")
            
        if not issues:
            issues.append("NO_OBVIOUS_ROUTING_ISSUES")
            details.append("Routing appears fine. Ensure your audio hardware device is selected in Preferences.")
            
        return {
            "diagnosis": issues,
            "details": " ".join(details)
        }
        
    def unmute_all(self):
        """Action command: Unmute all tracks including master."""
        self.execute_action("40339") # Action: Track: Unmute all tracks
        self.execute_action("40365") # Action: Track: Unmute master track
        logger.info("Unmuted all tracks and master.")
        
    def unsolo_all(self):
        """Action command: Unsolo all tracks."""
        self.execute_action("40340") # Action: Track: Unsolo all tracks
        logger.info("Unsoloed all tracks.")

if __name__ == "__main__":
    client = ReaperWebClient()
    print("Testing connection...")
    print(json.dumps(client.diagnose_audio(), indent=2))

