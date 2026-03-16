# Author: Tresslers Group
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MixNode:
    """
    Represents a single node (track, bus, etc.) in the mix topology graph.
    """
    def __init__(self, name: str, node_type: str = "track"):
        self.name = name
        self.node_type = node_type # track, bus, aux, master
        self.parent: Optional['MixNode'] = None
        self.children: List['MixNode'] = []
        self.fx_chain: List[str] = []
        self.sends: List[str] = []
        self.rms: float = 0.0
        self.lufs: float = 0.0
        self.spectral_profile: Dict[str, float] = {}
        self.stereo_width: float = 0.0
        self.track_index: int = -1

    def __repr__(self):
        return f"<MixNode {self.node_type}:{self.name}>"

class MixTopologyGraph:
    """
    Models the entire REAPER routing structure as a directed graph.
    """
    def __init__(self):
        self.nodes: Dict[str, MixNode] = {}
        self.master: Optional[MixNode] = None

    def build_from_state(self, project_state: Dict[str, Any]):
        """
        Constructs the graph from the live REAPER project state.
        """
        self.nodes = {}
        tracks = project_state.get('tracks', [])
        
        # 1. Create all nodes first
        for i, tr in enumerate(tracks):
            node = MixNode(tr['name'], node_type="track")
            node.track_index = i
            node.fx_chain = tr.get('fx', [])
            self.nodes[tr['name']] = node

        # 2. Establish hierarchy (folder tracks)
        # Note: REAPER tracks are a flat list, but 'is_folder' and 'folder_depth'
        # are used to determine nesting. For the MVP, we'll assume a simpler 
        # structure where parents are identified by track indices or name matching.
        
        # 3. Handle specific routing (e.g. Bus detection)
        for name, node in self.nodes.items():
            if "bus" in name.lower() or "group" in name.lower():
                node.node_type = "bus"
        
        # 4. Master node
        self.master = MixNode("Master", node_type="master")
        self.nodes["Master"] = self.master

    def get_bus_for_track(self, track_name: str) -> Optional[MixNode]:
        """Finds the parent bus for a given track."""
        node = self.nodes.get(track_name)
        if not node or not node.parent:
            # Fallback: check if any node with type 'bus' contains this track name in its children
            # (In a real implementation, this follows the REAPER folder hierarchy)
            return None
        return node.parent

    def get_summary(self) -> str:
        summary = []
        for name, node in self.nodes.items():
            if node.node_type == "bus":
                children = [c.name for c in node.children]
                summary.append(f"Bus: {name} (Children: {', '.join(children)})")
        return "\n".join(summary) if summary else "No buses detected."

