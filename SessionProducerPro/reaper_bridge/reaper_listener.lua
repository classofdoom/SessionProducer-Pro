-- Author: Tresslers Group
-- SessionProducer Pro - High-Performance Reaper Listener Bridge
-- Reads JSON commands from REAPER's ExtState instead of disk, 
-- eliminating file locks and CPU overhead.

local section_name = "SessionProducer"
local key_name = "Command"

function msg(m)
  reaper.ShowConsoleMsg(tostring(m) .. "\n")
end

-- Ramping state tracking for advanced automation
local active_ramps = {}

function url_decode(str)
  str = str:gsub("+", " ")
  str = str:gsub("%%(%x%x)", function(h) return string.char(tonumber(h, 16)) end)
  return str
end

function execute_command(json_str)
    if not json_str or json_str == "" then return end
    local action = json_str:match('"action"%s*:%s*"(.-)"')
    if not action then return end
    
    if action == "insert_track" then
        local track_name = json_str:match('"name"%s*:%s*"(.-)"') or "New Track"
        local count = reaper.CountTracks(0)
        reaper.InsertTrackAtIndex(count, true)
        local tr = reaper.GetTrack(0, count)
        if tr then
            reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", track_name, true)
            reaper.SetOnlyTrackSelected(tr)
            msg("Executed: Create Track -> " .. track_name)
        end
        
    elseif action == "set_tempo" then
        local bpm = json_str:match('"bpm"%s*:%s*([%d.]+)')
        if bpm then
            reaper.SetCurrentBPM(0, tonumber(bpm), true)
            msg("Executed: Set Tempo to " .. bpm)
        end
        
    elseif action == "delete_track" then
        local track_idx = tonumber(json_str:match('"track_index"%s*:%s*([%d.-]+)'))
        if track_idx then
            local tr = track_idx == -1 and reaper.GetTrack(0, reaper.CountTracks(0)-1) or reaper.GetTrack(0, track_idx)
            if tr then
                reaper.DeleteTrack(tr)
                msg("Executed: Delete Track")
            end
        end

    elseif action == "add_fx" then
        local track_idx = tonumber(json_str:match('"track_index"%s*:%s*([%d.-]+)')) or 0
        local fx_name = json_str:match('"fx_name"%s*:%s*"(.-)"')
        if fx_name then
            local tr = track_idx == -1 and reaper.GetTrack(0, reaper.CountTracks(0)-1) or reaper.GetTrack(0, track_idx)
            if tr then
                msg("Attempting to add FX: " .. fx_name)
                -- Try 1: Literal Match
                local success = reaper.TrackFX_AddByName(tr, fx_name, false, 1)
                
                -- Try 2: Aliases for common terms
                if success < 0 then
                    local fx_lower = fx_name:lower()
                    local aliases = {
                        ["reverb"] = "ReaVerb",
                        ["compressor"] = "ReaComp",
                        ["comp"] = "ReaComp",
                        ["eq"] = "ReaEQ",
                        ["delay"] = "ReaDelay",
                        ["tubescreamer"] = "JS: Guitar/TubeScreamer",
                        ["distortion"] = "JS: Guitar/TubeScreamer",
                        ["saturator"] = "JS: Utility/soft_clipper",
                        ["limiter"] = "ReaLimit",
                        ["chorus"] = "JS: Modulation/Chorus"
                    }
                    if aliases[fx_lower] then
                        msg("Alias found, trying: " .. aliases[fx_lower])
                        success = reaper.TrackFX_AddByName(tr, aliases[fx_lower], false, 1)
                    end
                end

                -- Try 3: Fuzzy/Partial (if not found)
                if success < 0 then
                    msg("No alias or literal match found, trying fuzzy search for: " .. fx_name)
                    success = reaper.TrackFX_AddByName(tr, fx_name, false, 1)
                end
                
                -- Try 3: Stripping prefixes if they were provided but failed
                if success < 0 and fx_name:find(":") then
                    local simple_name = fx_name:match(":%s*(.*)")
                    msg("Stripping prefix, trying: " .. simple_name)
                    success = reaper.TrackFX_AddByName(tr, simple_name, false, 1)
                end

                if success >= 0 then
                    msg("SUCCESS: Added FX -> " .. fx_name)
                else
                    msg("CRITICAL FAILED: Could not find/add FX -> " .. fx_name)
                    -- Fallback: If it's a Splice/Labs failure, try the other common one
                    if fx_name:lower():find("splice") then
                        msg("Entering Splice Fallback Loop...")
                        local splice_variants = {
                            "Splice INSTRUMENT (Splice)",
                            "VST3i: Splice INSTRUMENT (Splice)",
                            "Splice INSTRUMENT",
                            "VST3i: Splice INSTRUMENT",
                            "VST3i: Splice (Splice)",
                            "VST3i: Splice Bridge (Splice)"
                        }
                        for _, v in ipairs(splice_variants) do
                            local f_success = reaper.TrackFX_AddByName(tr, v, false, 1)
                            if f_success >= 0 then 
                                msg("SUCCESS: Found Splice variant -> " .. v)
                                break 
                            end
                        end
                    elseif fx_name:lower():find("labs") then
                        msg("Entering LABS Fallback Loop...")
                        local labs_variants = {
                            "VST3i: LABS (Spitfire Audio)",
                            "LABS (Spitfire Audio)",
                            "VST3i: LABS",
                            "VSTi: LABS",
                            "LABS"
                        }
                        for _, v in ipairs(labs_variants) do
                            local f_success = reaper.TrackFX_AddByName(tr, v, false, 1)
                            if f_success >= 0 then 
                                msg("SUCCESS: Found LABS variant -> " .. v)
                                break 
                            end
                        end
                    end
                    if reaper.TrackFX_GetCount(tr) == 0 then
                        msg("CRITICAL: All fallbacks failed for " .. fx_name .. ". Please check FX browser for exact name.")
                    end
                end
            end
        end

    elseif action == "insert_media" then
        local path = json_str:match('"path"%s*:%s*"(.-)"')
        local track_idx = tonumber(json_str:match('"track_index"%s*:%s*([%d.-]+)')) or 0
        local pos = tonumber(json_str:match('"position"%s*:%s*([%d.-]+)')) or 0
        
        if path then
            local tr = track_idx == -1 and reaper.GetTrack(0, reaper.CountTracks(0)-1) or reaper.GetTrack(0, track_idx)
            if tr then
                reaper.SetOnlyTrackSelected(tr)
                reaper.SetEditCurPos(pos, true, false)
                reaper.InsertMedia(path, 0)
                msg("Executed: Insert Media -> " .. path)
            end
        end

    elseif action == "set_pan" then
        local track_idx = tonumber(json_str:match('"track_index"%s*:%s*([%d.-]+)')) or 0
        local pan = tonumber(json_str:match('"pan"%s*:%s*([%d.-]+)')) or 0
        local tr = track_idx == -1 and reaper.GetTrack(0, reaper.CountTracks(0)-1) or reaper.GetTrack(0, track_idx)
        if tr then
            reaper.SetMediaTrackInfo_Value(tr, "D_PAN", pan)
            msg("Executed: Set Pan to " .. pan)
        end

    elseif action == "set_volume" then
        local track_idx = tonumber(json_str:match('"track_index"%s*:%s*([%d.-]+)')) or 0
        local vol = tonumber(json_str:match('"volume_db"%s*:%s*([%d.-]+)')) or 0
        local tr = track_idx == -1 and reaper.GetTrack(0, reaper.CountTracks(0)-1) or reaper.GetTrack(0, track_idx)
        if tr then
            local new_vol = 10^(vol/20)
            reaper.SetMediaTrackInfo_Value(tr, "D_VOL", new_vol)
            msg("Executed: Set Volume to " .. vol .. "dB")
        end

    elseif action == "set_fx_preset" then
        local track_idx = tonumber(json_str:match('"track_index"%s*:%s*([%d.-]+)')) or 0
        local fx_idx = tonumber(json_str:match('"fx_index"%s*:%s*([%d.-]+)')) or 0
        local preset_name = json_str:match('"preset_name"%s*:%s*"(.-)"')
        
        local tr = track_idx == -1 and reaper.GetTrack(0, reaper.CountTracks(0)-1) or reaper.GetTrack(0, track_idx)
        if tr and preset_name then
            -- Note: For some VSTs, TrackFX_SetPreset handles standard presets. 
            -- VST3 (.vstpreset) and AU (.aupreset) might require loading a chunk or navigating internal banks.
            -- This MVP uses the standard Reaper API.
            reaper.TrackFX_SetPreset(tr, fx_idx, preset_name)
            msg("Executed: Set FX Preset -> " .. preset_name .. " on track " .. track_idx)
        end
        
    elseif action == "ramp_volume" then
        local track_idx = tonumber(json_str:match('"track_index"%s*:%s*([%d.-]+)')) or 0
        local start_db = tonumber(json_str:match('"start_db"%s*:%s*([%d.-]+)')) or 0
        local end_db = tonumber(json_str:match('"end_db"%s*:%s*([%d.-]+)')) or -6
        local duration = tonumber(json_str:match('"duration"%s*:%s*([%d.-]+)')) or 0.5
        
        local tr = track_idx == -1 and reaper.GetTrack(0, reaper.CountTracks(0)-1) or reaper.GetTrack(0, track_idx)
        if tr then
            -- Kick off a native smooth volume ramp in the defer loop
            table.insert(active_ramps, {
                track = tr,
                start_db = start_db,
                end_db = end_db,
                start_time = reaper.time_precise(),
                duration = duration
            })
            msg("Executed: Ramp Volume Scheduled -> " .. end_db .. "dB over " .. duration .. "s")
        end

    elseif action == "transport_play" then
        reaper.OnPlayButton()
    elseif action == "transport_stop" then
        reaper.OnStopButton()
    elseif action == "open_preferences" then
        reaper.Main_OnCommand(40016, 0)
    end
end

function process_ramps()
    if #active_ramps == 0 then return end
    local now = reaper.time_precise()
    
    for i = #active_ramps, 1, -1 do
        local ramp = active_ramps[i]
        local elapsed = now - ramp.start_time
        local progress = elapsed / ramp.duration
        
        if progress >= 1.0 then
            progress = 1.0
            table.remove(active_ramps, i)
        end
        
        -- Interpolate db
        local current_db = ramp.start_db + (ramp.end_db - ramp.start_db) * progress
        local current_vol_ratio = 10^(current_db/20)
        reaper.SetMediaTrackInfo_Value(ramp.track, "D_VOL", current_vol_ratio)
    end
end

function main()
    -- Smooth processing of internal automations
    process_ramps()

    if reaper.HasExtState(section_name, key_name) then
        local content = reaper.GetExtState(section_name, key_name)
        if content and #content > 0 then
            -- Decode the URL-encoded JSON before processing
            content = url_decode(content)
            msg("New command detected: " .. content)
            -- Clear it instantly so we only execute once
            reaper.SetExtState(section_name, key_name, "", false)
            
            local status, err = pcall(execute_command, content)
            if not status then
                msg("Error executing command: " .. err)
            end
        end
    end
    
    reaper.defer(main)
end

msg("SessionProducer Pro Listener Started (ExtState Mode)...")
main()

