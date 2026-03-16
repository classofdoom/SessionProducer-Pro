# Author: Tresslers Group

import logging
from typing import List
from ai.strategy_engine import ProductionStrategy
from reaper_bridge.command_writer import CommandWriter

logger = logging.getLogger(__name__)

class ExecutionLayer:
    """
    Translates ProductionStrategy objects into specific REAPER actions.
    """
    
    def __init__(self, command_writer: CommandWriter, spl_router=None, spl_mapper=None, spl_gen=None):
        self.cmd = command_writer
        self.spl_router = spl_router
        self.spl_mapper = spl_mapper
        self.spl_gen = spl_gen

    def execute(self, strategy: ProductionStrategy):
        logger.info(f"ExecutionLayer received strategies: {strategy.strategies}")
        
        results = []
        intent = strategy.intent
        
        # Reset mapper memory for new session diversity
        if hasattr(self, 'spl_mapper'):
            self.spl_mapper.reset_session()
        
        # 2. Strategy Processing Loop
        tracks_to_delete = set()
        
        strat_list = strategy.strategies or []
        if not isinstance(strat_list, list): strat_list = []
        for move in strat_list:
            # Handle Dict-based strategies (Phase 18 Elite Mode)
            if isinstance(move, dict):
                move_type = move.get("type", "").lower()
                params = move.get("parameters", {})
                
                if any(k in move_type for k in ["generation", "chord", "melody", "drum", "texture", "epic", "cinematic", "beauty", "conductor"]):
                    if hasattr(self, 'spl_router') and hasattr(self, 'spl_mapper') and hasattr(self, 'spl_gen'):
                        # 1. Map to Preset (or use suggested instrument)
                        suggested_inst = params.get("instrument", intent.raw_text)
                        mapping = self.spl_mapper.map_prompt(suggested_inst)
                        
                        if mapping["success"]:
                            preset = mapping["match"]
                            
                            # BPM-Aware Arrangement: Fetch current project BPM for accurate bar-to-second mapping
                            try:
                                bpm = self.cmd.reaper.get_bpm()
                                if bpm <= 10.0: # Safeguard against 0 or unrealistic values
                                    bpm = 120.0
                            except Exception as e:
                                logger.warning(f"Failed to fetch BPM, defaulting to 120. Error: {e}")
                                bpm = 120.0
                                
                            start_bar = params.get("start_bar", 0)
                            # 1 Bar = 4 Beats. Seconds = Beats * (60 / BPM)
                            section_start_seconds = (start_bar * 4.0) * (60.0 / bpm)
                            
                            gen_params = {
                                "instrument_type": preset["instrument_type"],
                                "key": intent.parameters.get("key") or "C major",
                                "humanization": mapping["humanization"],
                                "move_type": move_type,
                                **params # Inject AI's specific musical parameters (chords, scale, etc.)
                            }
                            notes, ccs = self.spl_gen.generate_sequence(gen_params)
                            
                            # Apply Zimmer Crescendo: If requested, ramp up CC1/CC11 over the section
                            if params.get("cc_crescendo"):
                                curve = params.get("dynamic_curve", "linear")
                                start_val = 0.1 if curve == "dramatic" else 0.3
                                
                                for cc in ccs:
                                    total_len = max(0.1, params.get("bars", 8) * 4.0)
                                    norm_time = min(1.0, cc.time / total_len)
                                    # Exponential ramp for dramatic effect
                                    multiplier = norm_time ** 2 if curve == "dramatic" else norm_time
                                    cc.value = int(cc.value * (start_val + (multiplier * (1.0 - start_val))))

                            # 3. Insert to REAPER with Spatial Context
                            track_name = f"SPL {preset['preset_name']}"
                            self.spl_router.insert_generative_instrument(
                                track_name=track_name,
                                asset_match=preset,
                                midi_data=(notes, ccs),
                                section_start=section_start_seconds,
                                fx_chain=params.get("fx_chain", []),
                                spatial_params={
                                    "stereo_width": params.get("stereo_width"),
                                    "reverb_size": params.get("reverb_size")
                                }
                            )
                            results.append(f"Deployed {preset['preset_name']} at Bar {start_bar}.")
                            # Add a small delay for large orchestral templates if needed
                            import time
                            if len(strategy.strategies) > 4: time.sleep(0.5)
                        else:
                            results.append(f"Could not find SPL instrument for: {suggested_inst}")
                    continue
                else:
                    # Treat unknown dicts as strings if possible or skip
                    move = str(move)

            # Handle String-based strategies
            move_lower = move.lower()
            
            # Deletion Pre-processing
            if any(k in move_lower for k in ["delete", "remove", "deletion"]):
                for target in intent.target_tracks:
                    import re
                    match = re.search(r'(?:track\s*)?(\d+)', target.lower())
                    if match:
                        try:
                            idx = int(match.group(1)) - 1
                            if idx >= 0: tracks_to_delete.add(idx)
                        except ValueError: continue

            # Track Creation
            elif any(k in move_lower for k in ["setup", "create", "insert", "add track"]):
                if intent.target_tracks:
                    for track_name in intent.target_tracks:
                        self.cmd.create_track(track_name)
                        results.append(f"Created track: {track_name}")
                        import time
                        time.sleep(0.1)
                else:
                    self.cmd.create_track("New Production Track")
                    results.append("Created default production track.")

            # Mixing
            elif "wider" in move_lower or "stereo" in move_lower:
                for target in intent.target_tracks:
                    self.cmd.set_pan(0, 0.5) 
                    results.append(f"Widened {target} via OSC panner.")
                
            elif "masking" in move_lower or "cleanup" in move_lower:
                for target in intent.target_tracks:
                    self.cmd.add_fx(0, "ReaEQ")
                    results.append(f"Applied cleanup EQ to {target}.")

            elif "duck" in move_lower or "volume" in move_lower:
                self.cmd.duck_track(0, db=-6.0)
                results.append("Applied sidechain ducking.")

            if "tempo" in move_lower or "bpm" in move_lower:
                bpm = intent.parameters.get("bpm", 120)
                self.cmd.set_tempo(int(bpm))
                results.append(f"Set project tempo to {bpm} BPM.")

            # Troubleshooting
            if "diagnose_audio" in move_lower:
                self.cmd.diagnose_audio()
                results.append("Initiated audio diagnosis scan in REAPER.")

            if "open_preferences" in move_lower:
                self.cmd.open_preferences()
                results.append("Opened REAPER Preferences (Audio Device).")

        # 3. Finalization logic
        if tracks_to_delete:
            sorted_deletions = sorted(list(tracks_to_delete), reverse=True)
            for idx in sorted_deletions:
                self.cmd.delete_track_by_index(idx)
                results.append(f"Deleted track {idx+1}")
                import time
                time.sleep(0.15)

        # Handle Playback (Once at the end if anything was generated)
        if any("Generated" in r for r in results):
            import time
            time.sleep(0.5)
            self.spl_router.play_session()
            results.append("Started playback.")

        # Deduplicate results
        unique_results = []
        seen = set()
        for r in results:
            if r not in seen:
                unique_results.append(r)
                seen.add(r)

        if not unique_results:
             return "Strategy processed but no concrete REAPER actions were triggered."

        return "Successfully executed: " + " | ".join(unique_results)

