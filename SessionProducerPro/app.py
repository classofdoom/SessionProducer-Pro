# Author: Tresslers Group

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from ui.asset_browser_panel import AssetBrowserPanel

# Backend Imports
from asset_engine.asset_indexer import AssetIndexer
from reaper_bridge.command_writer import CommandWriter
from ai.intent_classifier import IntentClassifier
from ai.strategy_engine import StrategyEngine
from production_engine.execution_layer import ExecutionLayer
from state.reaper_state_sync import ReaperStateWatcher

# Mixing Phase 2 Imports
from mixing.mix_topology_graph import MixTopologyGraph
from mixing.masking_engine import MaskingEngine
from mixing.energy_curve_engine import EnergyCurveEngine
from mixing.mix_simulator import MixSimulator
from mixing.mix_bus_guardian import MixBusGuardian

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting SessionProducer Pro [Elite Mix Mode]...")
    
    app = QApplication(sys.argv)
    
    # Initialize Backend logic
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "assets.db")
    cmd_file_path = os.path.join(base_dir, "reaper_bridge", "commands.json")
    state_file_path = os.path.join(base_dir, "reaper_bridge", "state.json")
    
    indexer = AssetIndexer(db_path)
    cmd_writer = CommandWriter()
    state_watcher = ReaperStateWatcher(state_file_path)
    
    # Phase 2 Mixing Engines
    topology = MixTopologyGraph()
    masking = MaskingEngine()
    energy = EnergyCurveEngine()
    simulator = MixSimulator()
    guardian = MixBusGuardian()
    
    # Path A Personalization
    from ai.user_profile import UserProfile
    from ai.track_personality import TrackPersonality
    config_dir = os.path.join(base_dir, "config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    profile = UserProfile(os.path.join(config_dir, "user_profile.json"))
    memory = TrackPersonality()
    
    # Phase 16 SPL Integration
    from spl_integration.asset_indexer import SPLAssetIndexer
    from spl_integration.text_to_preset import TextToPresetMapper
    from spl_integration.midi_generator_v2 import MidiGeneratorV2
    from spl_integration.reaper_router import ReaperRouter
    
    spl_db_path = os.path.join(base_dir, "spl_assets.db")
    spl_indexer = SPLAssetIndexer(spl_db_path)
    spl_mapper = TextToPresetMapper(spl_indexer)
    spl_gen_v2 = MidiGeneratorV2()
    spl_router = ReaperRouter(cmd_writer, state_watcher)
    
    # Dry-run scan (Placeholder paths - User would configure these)
    # spl_indexer.scan_directories(["C:/Users/User/Documents/Spitfire"]) 

    # Generative helpers
    from production_engine.midi_generator import MidiGenerator
    from production_engine.arrangement_engine import ArrangementEngine
    midi_gen = MidiGenerator()
    arrangement = ArrangementEngine(spl_gen_v2) # Connect it to the V2 generator

    # Phase 18 Mastering & Elite Intelligence
    from production_engine.mastering_engine import MasteringEngine
    mastering = MasteringEngine()

    # Thinking Pipeline (Path A + Phase 2 + Phase 16 + Phase 18)
    classifier = IntentClassifier()
    strategy_eng = StrategyEngine(
        user_profile=profile, 
        track_personality=memory,
        topology=topology,
        masking=masking,
        energy=energy,
        mastering=mastering,
        arrangement_engine=arrangement # Inject here
    )
    # Inject mastering and theory knowledge (theory is internal to spl_gen/strategy)
    executor = ExecutionLayer(cmd_writer, spl_router=spl_router, spl_mapper=spl_mapper, spl_gen=spl_gen_v2)
    
    # Initialize UI
    window = MainWindow()
    asset_panel = window.asset_panel
    # window.splitter.setSizes([450, 750]) # Handled in MainWindow now

    # State Polling Timer (300ms)
    def poll_reaper():
        state = state_watcher.poll()
        if state:
            # Update Topology Graph
            topology.build_from_state(state)
            
            # Guardian Check
            master_info = next((t for t in state.get('tracks', []) if t['name'].lower() == 'master'), {})
            compliance = guardian.check_compliance(master_info)
            
            status_msg = f"Reaper Sync: {len(state.get('tracks', []))} tracks | BPM: {state.get('bpm', 120)} | {compliance['summary']}"
            window.statusBar().showMessage(status_msg)

    timer = QTimer()
    timer.timeout.connect(poll_reaper)
    timer.start(300) 

    # Connect UI signals
    def run_scans():
        window.chat_panel.append_message("System", "Initiating global asset scan...")
        
        # Load SPL Config
        spl_config_path = os.path.join(base_dir, "config", "spl_config.json")
        spitfire_paths = []
        file_patterns = [".patches", ".nki"]
        
        if os.path.exists(spl_config_path):
            try:
                import json
                with open(spl_config_path, 'r') as f:
                    config = json.load(f)
                    spitfire_paths = config.get("spitfire_paths", [])
                    file_patterns = config.get("file_patterns", [".patches", ".nki"])
            except Exception as e:
                logger.error(f"Failed to load SPL config: {e}")
        
        # Fallback if config empty
        if not spitfire_paths:
             spitfire_paths = [os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "Spitfire")]

        # Combine all configured paths for the SPL indexer
        all_spl_paths = spitfire_paths + config.get("splice_paths", [])

        # 1. SPL Assets
        spl_indexer.scan_directories(all_spl_paths, file_patterns=file_patterns)
        
        # 2. Update UI
        asset_panel.tree.clear()
        
        # Load from SPL Index
        spl_assets = spl_indexer.query_assets()
        for asset in spl_assets:
            asset_panel.add_asset({
                "filename": asset["preset_name"],
                "bpm": "-",
                "key": "-",
                "category": f"SPL {asset['instrument_type']}"
            })
            
        window.chat_panel.append_message("System", f"Scan complete. Indexed {len(spl_assets)} SPL instruments.")

    asset_panel.scan_requested.connect(run_scans)

    def handle_user_message(text):
        logger.info(f"User Request: {text}")
        context = state_watcher.get_context_summary()
        current_state = state_watcher.current_state
        
        # 1. Intent Classification
        intent = classifier.classify(text, project_context=context)
        window.chat_panel.append_message("System", f"Intent: {intent.category} ({intent.confidence:.2f})")
        
        # 2. Strategy Development
        strategy = strategy_eng.develop_strategy(intent, project_context=context, state_data=current_state)
        
        # 3. Confidence Check / Multi-Option Handling
        if strategy.confidence < 0.75 and strategy.options:
            # For arrangement/generative, if options exist, we can be more proactive 
            # or just show them. For now, let's show them and use the first as default 
            # unless the user request was very vague.
            if intent.category in ["arrangement", "generative"]:
                 window.chat_panel.append_message("System", f"Confidence moderately low ({strategy.confidence:.2f}). Proceeding with Best Match: {strategy.options[0]['label']}")
                 strategy.strategies = strategy.options[0].get('strategies', [])
            else:
                window.chat_panel.append_message("System", "Confidence is low. Please select an option:")
                for opt in strategy.options:
                    window.chat_panel.append_message("System", f"- [{opt['label']}]: {opt['explanation']}")
                return # Await user selection for high-stakes mix moves

        if strategy.reasoning:
            window.chat_panel.append_message("System", f"Strategy: {strategy.reasoning}")
            
        # 4. Simulation Layer (Mandatory)
        if intent.category in ["mixing", "spatial", "energy"]:
            if not simulator.validate_strategy(strategy.strategies, current_state):
                window.chat_panel.append_message("System", "Safety Refusal: Simulation failed headroom/safety checks.")
                return
            window.chat_panel.append_message("System", "Simulation: Passed safety checks.")

        # 5. Execution
        result = executor.execute(strategy)
        window.chat_panel.append_message("System", result)

    # Phase 19 Voice Integration
    from ai.voice_handler import VoiceHandler
    voice_handler = VoiceHandler()
    
    def on_voice_ready(text):
        window.chat_panel.msg_input.setText(text)
        window.chat_panel.set_recording_state(False)
        window.chat_panel.append_message("System", f"Voice detected: {text}")
        # Auto-send if successful? For now let user review
        
    def on_voice_error(error):
        window.chat_panel.set_recording_state(False)
        window.chat_panel.append_message("System", f"Voice Error: {error}")

    def handle_mic_request():
        window.chat_panel.set_recording_state(True)
        window.chat_panel.append_message("System", "Mic active. Listening for 5 seconds...")
        voice_handler.start_listening(on_voice_ready, on_voice_error)

    window.chat_panel.mic_requested.connect(handle_mic_request)
    window.chat_panel.message_sent.connect(handle_user_message)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


