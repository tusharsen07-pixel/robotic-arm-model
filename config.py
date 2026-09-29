# ============================================================
# config.py — Central configuration for AI Robotic Arm
# All hardware values and tunable parameters live here.
# Load secrets from environment variables, never hard-coded.
# ============================================================

import os
import logging
from pathlib import Path

# Load .env file if python-dotenv is installed (development convenience)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Project paths ────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
LOG_DIR  = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ── Runtime mode ─────────────────────────────────────────────
# Set SIMULATION_MODE=false in .env when real hardware is connected.
SIMULATION_MODE: bool = os.getenv("SIMULATION_MODE", "true").lower() in ("true", "1", "yes")

# ── Logging ──────────────────────────────────────────────────
LOG_LEVEL_STR: str = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL: int = getattr(logging, LOG_LEVEL_STR, logging.INFO)

# ── Gemini AI (Optional / Future Cloud Module) ───────────────
# Gemini is NOT required. The main arm control runs 100% locally.
# Kept strictly for optional future cloud features.
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL:   str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# ── ESP32 / Serial ───────────────────────────────────────────
ESP32_PORT:    str = os.getenv("ESP32_PORT", "COM3")
ESP32_BAUD:    int = int(os.getenv("ESP32_BAUD", "115200"))
ESP32_TIMEOUT: float = 5.0   # seconds to wait for a response

# ── Camera ───────────────────────────────────────────────────
CAMERA_INDEX:     int  = int(os.getenv("CAMERA_INDEX", "0"))
CAMERA_WIDTH:     int  = 640
CAMERA_HEIGHT:    int  = 480
CAMERA_FPS:       int  = 30

# ── Servo / Robot arm ────────────────────────────────────────
# Joint indices on PCA9685 (filled after hardware calibration)
SERVO_CHANNELS = {
    "base":       0,
    "shoulder":   1,
    "elbow":      2,
    "wrist_pitch":3,
    "wrist_roll": 4,
    "gripper":    5,
}

# Safe angular limits per joint  [min_deg, max_deg]
JOINT_LIMITS = {
    "base":        [0,   180],
    "shoulder":    [15,  165],
    "elbow":       [15,  165],
    "wrist_pitch": [0,   180],
    "wrist_roll":  [0,   180],
    "gripper":     [0,    90],   # 0 = open, 90 = closed
}

# Predefined safe poses  {joint_name: angle_deg}
SAFE_POSES = {
    "HOME": {
        "base": 90, "shoulder": 90, "elbow": 90,
        "wrist_pitch": 90, "wrist_roll": 90, "gripper": 0,
    },
    "PICK": {
        "base": 90, "shoulder": 45, "elbow": 120,
        "wrist_pitch": 90, "wrist_roll": 90, "gripper": 0,
    },
    "PLACE_LEFT": {
        "base": 30, "shoulder": 60, "elbow": 100,
        "wrist_pitch": 90, "wrist_roll": 90, "gripper": 80,
    },
    "PLACE_RIGHT": {
        "base": 150, "shoulder": 60, "elbow": 100,
        "wrist_pitch": 90, "wrist_roll": 90, "gripper": 80,
    },
    "GRIP_OPEN": {
        "gripper": 0,
    },
    "GRIP_CLOSE": {
        "gripper": 80,
    },
}

# Robot arm physical dimensions (mm) — update after hardware measurement
ARM_LINK_1_MM: float = 150.0   # shoulder → elbow
ARM_LINK_2_MM: float = 150.0   # elbow → wrist
ARM_BASE_HEIGHT_MM: float = 80.0

# ── Voice / STT ──────────────────────────────────────────────
STT_ENGINE:        str = "vosk"          # "vosk" | "whisper"
VOSK_MODEL_PATH:   str = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-en-us")
WAKE_WORD:         str = "hey robot"
AUDIO_SAMPLE_RATE: int = 16000
AUDIO_CHANNELS:    int = 1

# ── Text-to-Speech ───────────────────────────────────────────
TTS_ENGINE: str = "pyttsx3"   # "pyttsx3" (offline) | "gtts" (online)

# ── Safety ───────────────────────────────────────────────────
EMERGENCY_STOP_ENABLED: bool = True
MAX_CONSECUTIVE_ERRORS:  int  = 3    # auto-stop after N consecutive errors
COMMAND_TIMEOUT_SEC:     float = 10.0
