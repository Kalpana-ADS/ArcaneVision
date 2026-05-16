# 🔮 ArcaneVision – AI Magical Hand Gesture System

> **Real-time webcam magic powered by Computer Vision.** Cast spells by moving your hands — Doctor Strange style.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-red)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-yellow)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## ✨ Features

| Feature | Detail |
|---------|--------|
| 🖐 Real-time hand tracking | MediaPipe Hands (up to 2 hands, 21 landmarks each) |
| 🧙 10 magical spells | Unique particle effects for every spell |
| ⚡ Particle system | CPU particle engine simulating thousands of particles |
| 🎨 Cinematic rendering | Glow, alpha blending, additive compositing |
| 📊 Live HUD | FPS, gesture name, spell name, hand count |
| ⌨️ Keyboard controls | Instant spell switching for demos |
| 🔊 Sound support | Pygame mixer integration |
| 🏗️ Modular OOP | MVC-style architecture, no circular imports |

---

## 🔮 The 10 Spells

| # | Key | Gesture | Spell | Effect |
|---|-----|---------|-------|--------|
| 1 | `1` | Open Palm | ✨ Fairy Dust | Golden sparkle burst + floating particles |
| 2 | `2` | Closed Fist | 🔥 Fireball | Fire projectile with explosion |
| 3 | `3` | Pointing | ❄️ Ice Freeze | Frost overlay + ice crystal shards |
| 4 | `4` | Peace Sign | ⚡ Lightning | Electric arcs between fingers |
| 5 | `5` | Pinch | 🌀 Portal | Doctor Strange rotating vortex |
| 6 | `6` | Spread | 🌬️ Levitation | Floating orbs + wind streams |
| 7 | `7` | Thumbs Up | 💚 Healing Aura | Green pulse rings + rising orbs |
| 8 | `8` | OK Sign | 🌑 Shadow Magic | Dark smoke tendrils + vignette |
| 9 | `9` | Vulcan Salute | ⏸️ Time Freeze | Desaturated screen + clock rings |
| 0 | `0` | Horns | 🐉 Summon Dragon | Animated procedural dragon |

---

## 📁 Project Structure

```
arcanevision/
├── src/
│   ├── main.py                    # Entry point
│   ├── core/
│   │   ├── engine.py              # Main game loop + orchestrator
│   │   ├── types.py               # Shared dataclasses (NO circular imports)
│   │   └── config.py              # All constants and tuning
│   ├── gestures/
│   │   ├── hand_tracker.py        # MediaPipe wrapper
│   │   └── gesture_recognizer.py  # Rule-based gesture classifier
│   ├── spells/
│   │   ├── base_spell.py          # Abstract base class
│   │   ├── fairy_spell.py
│   │   ├── fire_spell.py
│   │   ├── ice_spell.py
│   │   ├── lightning_spell.py
│   │   ├── portal_spell.py
│   │   ├── levitation_spell.py
│   │   ├── healing_spell.py
│   │   ├── shadow_spell.py
│   │   ├── time_spell.py
│   │   └── dragon_spell.py
│   ├── effects/
│   │   ├── particles.py           # Particle factory helpers
│   │   └── renderer.py            # CV→Pygame bridge
│   ├── ui/
│   │   └── hud.py                 # HUD overlay
│   └── utils/
│       └── logger.py              # Logging setup
├── assets/
│   ├── sounds/                    # .wav/.ogg spell sounds (optional)
│   ├── sprites/                   # Sprite sheets (optional)
│   └── textures/                  # Overlay textures (optional)
├── requirements.txt
├── run.bat                        # Windows launcher
├── run.sh                         # Linux/macOS launcher
└── README.md
```

---

## 🚀 Installation & Running

### Windows (recommended: VS Code + PowerShell)

```powershell
# 1. Install Python 3.10+ from https://python.org
#    ✅ Check "Add Python to PATH" during install

# 2. Clone / download the project
cd C:\Projects\arcanevision

# 3. Create virtual environment
python -m venv venv

# 4. Activate it
venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run!
python -m src.main
```

Or just double-click **`run.bat`**.

### Linux / macOS

```bash
cd ~/projects/arcanevision
chmod +x run.sh
./run.sh
```

Or manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

---

## ⌨️ Controls

| Key | Action |
|-----|--------|
| `1` – `0` | Instantly cast spells 1-10 |
| `D` | Toggle debug skeleton overlay |
| `Q` / `Esc` | Quit |

### Gesture Controls (hold 0.4s to fire)

| Gesture | Description |
|---------|-------------|
| Open palm (all fingers extended) | Fairy Dust |
| Closed fist | Fireball |
| Index finger pointing | Ice Freeze |
| Peace sign (index + middle) | Lightning |
| Pinch (thumb + index close) | Portal |
| Spider-Man hand (index + pinky + thumb) | Levitation |
| Thumbs up | Healing |
| OK sign | Shadow Magic |
| Vulcan salute (split between middle & ring) | Time Freeze |
| Horns (index + pinky) | Dragon |

---

## 🔧 Troubleshooting

### Webcam not found
```
RuntimeError: Webcam 0 not available.
```
- Try changing `WEBCAM_INDEX = 1` (or 2) in `src/core/config.py`
- On Linux: check `ls /dev/video*`
- On Windows: open Device Manager → Cameras

### MediaPipe import error
```
ModuleNotFoundError: No module named 'mediapipe'
```
```bash
pip install mediapipe --upgrade
```
> Note: MediaPipe requires Python 3.8–3.11. Python 3.12 may have issues.

### Low FPS
- Reduce `WINDOW_WIDTH/HEIGHT` in `config.py` (try 960×540)
- Set `MP_MODEL_COMPLEXITY = 0` for faster tracking
- Reduce `MAX_PARTICLES` from 3000 to 1000

### Pygame display error (headless server)
```bash
export DISPLAY=:0  # Linux
```

### Python version
```bash
python --version  # Must be 3.10+
```

---

## 🏗️ Architecture Notes

- **`types.py`** is the single source of truth for all shared dataclasses. No module imports from another module in a way that creates cycles.
- **`engine.py`** is the orchestrator — it owns the loop, webcam, and spell registry.
- Each **spell** is self-contained: it owns its particle list and only receives a `RenderContext` snapshot.
- **Gesture recognition** is purely rule-based but the `classify()` method can be swapped for an ML model.

---

## 🎓 Credits & License

Built as a final-year / hackathon showcase project.  
MIT License — free to use, fork, and extend.
