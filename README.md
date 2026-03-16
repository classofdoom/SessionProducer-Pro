# SessionProducer Pro: AI Music Conductor & Producer

**Author**: Tresslers Group

SessionProducer Pro is an elite AI-driven music generation and arrangement engine designed for **REAPER**. It transforms natural language prompts into professional, multi-layered musical compositions, managing everything from MIDI generation and music theory to VST mapping and spatial production.

---

## 🎹 Core Capabilities

### 1. The Conductor V3 (Musical Intelligence)
The heart of the system is the **Conductor V3**, which moves beyond mechanical MIDI to produce human-like performances:
- **Phrased Evolution**: Melodic motifs transform every bar/phrase to prevent repetition.
- **Melodic Breathing**: AI strategically inserts musical rests for natural phrasing.
- **Organic Expression**: Adds "Chaos Jitter" to CC1 (Mod Wheel) and CC11 (Expression) to simulate human imperfection.
- **Dynamic Drum Fills**: Automatic snare/tom flourishes at phrase transitions.

### 2. Multi-Archetype Arrangement Engine
Automates the orchestration of full sessions based on genre archetypes:
- **Epic Fantasy**: A 5-section journey (Intro -> Exploration -> Tension -> Battle -> Resolution) with heavy layering (Brass, Strings, Taiko, Choir).
- **Lofi / Neosoul**: Professional 5-layer "Chill" stacking (Dusty Rhodes, Soul Bass, Clean Guitar, Hiphop Drums, Vinyl Texture) at 85 BPM.
- **The Zimmer Build**: Implements staggered track entries and exponential $t^2$ volume ramps for massive crescendos.

### 3. Tactical REAPER Integration
- **Execution Layer**: Translates AI strategies into native REAPER commands (ExtState Bridge).
- **FX Mapping Hardening**: A Lua-side alias engine resolves generic terms (e.g., "Reverb") to precise native plugins (`ReaVerb`).
- **Temporal Alignment**: Maps user time-markers (e.g., "Intro at 0:30") to precise project bars.
- **Spatial Controls**: Native support for **Stereo Width** and **Reverb Size** per track.

---

## 🛠️ Installation & Setup

### Prerequisites
1. **REAPER**: The primary workstation.
2. **Ollama**: Running locally with `gemma2:9b` (recommended) or `llama3`.
3. **Python 3.10+**

### Configuration
1. **Clone & Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **REAPER Bridge Activation:**
   - In REAPER, load and RUN `SessionProducerPro/reaper_bridge/reaper_listener.lua`.
   - Ensure the listener console says: *"SessionProducer Pro Listener Started..."*
3. **OSC Configuration:**
   - REAPER > Preferences > Control/OSC.
   - Add "Simple OSC" on Port `8000` (Localhost: `127.0.0.1`).

---

## 🚀 Usage Guide

| Category | Example Prompt |
| :--- | :--- |
| **Generative** | "Compose a lush cinematic intro in G major with a piano and cello." |
| **Arrangement** | "Create an epic fantasy battle climax at 2:30." |
| **Lofi / Chill** | "Chill Neosoul Lofi with a great electric guitar line and a sweet drum setup." |
| **Mixing** | "Make the vocal wider", "Duck the bass by 6dB whenever the kick hits". |

---

## 🏗️ Architecture

- **`app.py`**: The central coordinator and intent router.
- **`production_engine/`**: Arrangement, MIDI generation, and mastering logic.
- **`ai/`**: Intent classification and high-level strategy development.
- **`reaper_bridge/`**: High-performance background listener for REAPER via ExtState.
- **`ui/`**: Premium interface with real-time session telemetry.

---

## 🛠️ Bugs & Contributions

**SessionProducer Pro** is an evolving, experimental platform. Like any complex AI-driven system, you may encounter bugs or edge cases. 

We believe in the power of the open-source community:
- **Found a bug?** Open an issue.
- **Have an improvement?** Pull requests are more than welcome.
- **Want to add a genre?** We encourage you to fork, experiment, and help us turn this into the ultimate production assistant.

*Anyone is free to change, improve, and evolve the codebase under the terms of the MIT License.*

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

*Created with ❤️ by Tresslers Group.*
