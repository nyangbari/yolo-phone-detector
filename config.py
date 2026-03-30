from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_NAME = "yolo26s.pt"
DEFAULT_MODEL_PATH = APP_DIR / "models" / DEFAULT_MODEL_NAME


def resolve_model_path(model_path: str) -> str:
    candidate = Path(model_path).expanduser()
    if candidate.is_absolute():
        return str(candidate)

    search_paths = [
        Path.cwd() / candidate,
        APP_DIR / candidate,
    ]
    if len(candidate.parts) == 1:
        search_paths.append(APP_DIR / "models" / candidate)

    for resolved in search_paths:
        if resolved.exists():
            return str(resolved.resolve())

    if len(candidate.parts) == 1:
        return str((APP_DIR / "models" / candidate).resolve())
    return str((APP_DIR / candidate).resolve())


@dataclass(slots=True)
class AppConfig:
    model_path: str = DEFAULT_MODEL_NAME
    camera_mode: str = "usb"
    camera_index: int = 0
    camera_sensor_id: int = 0
    camera_width: int = 1280
    camera_height: int = 720
    camera_fps: int = 30
    camera_flip_method: int = 0
    confidence_threshold: float = 0.45
    min_box_area_ratio: float = 0.012
    cooldown_seconds: float = 4.0
    streak_required: int = 8
    camera_retries: int = 5
    target_labels: set[str] = field(default_factory=lambda: {"cell phone"})
    overlay_labels: set[str] = field(default_factory=lambda: {"cell phone"})
    history_limit: int = 6
    panel_width: int = 360
    window_name: str = "Focus Guard"


def parse_args() -> AppConfig:
    parser = argparse.ArgumentParser(
        description="Watch the webcam for phones and log an alert when one is detected."
    )
    parser.add_argument("--model", default=DEFAULT_MODEL_NAME, help="Path to a YOLO model file.")
    parser.add_argument(
        "--camera-mode",
        choices=("usb", "csi"),
        default="usb",
        help="Camera capture backend. Use 'csi' for Jetson CSI cameras like IMX219.",
    )
    parser.add_argument("--camera-index", type=int, default=0, help="Camera index to open.")
    parser.add_argument("--camera-sensor-id", type=int, default=0, help="Jetson CSI sensor-id for nvarguscamerasrc.")
    parser.add_argument("--camera-width", type=int, default=1280, help="Requested camera capture width.")
    parser.add_argument("--camera-height", type=int, default=720, help="Requested camera capture height.")
    parser.add_argument("--camera-fps", type=int, default=30, help="Requested camera frames per second.")
    parser.add_argument(
        "--camera-flip-method",
        type=int,
        default=0,
        help="Jetson nvvidconv flip-method value to rotate or mirror the CSI camera image.",
    )
    parser.add_argument("--confidence", type=float, default=0.45, help="Minimum confidence to accept.")
    parser.add_argument(
        "--min-area-ratio",
        type=float,
        default=0.012,
        help="Minimum fraction of the frame the detection box must occupy.",
    )
    parser.add_argument(
        "--cooldown",
        type=float,
        default=4.0,
        help="Seconds to wait between alerts.",
    )
    parser.add_argument(
        "--streak",
        type=int,
        default=8,
        help="Consecutive qualifying frames required before alerting.",
    )
    parser.add_argument(
        "--camera-retries",
        type=int,
        default=5,
        help="How many times to retry opening the camera.",
    )
    args = parser.parse_args()

    return AppConfig(
        model_path=resolve_model_path(args.model),
        camera_mode=args.camera_mode,
        camera_index=args.camera_index,
        camera_sensor_id=args.camera_sensor_id,
        camera_width=args.camera_width,
        camera_height=args.camera_height,
        camera_fps=args.camera_fps,
        camera_flip_method=args.camera_flip_method,
        confidence_threshold=args.confidence,
        min_box_area_ratio=args.min_area_ratio,
        cooldown_seconds=args.cooldown,
        streak_required=args.streak,
        camera_retries=args.camera_retries,
    )
