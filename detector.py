from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config import AppConfig


@dataclass(slots=True)
class DetectionSummary:
    annotated_frame: object
    target_visible: bool
    target_count: int


class PhoneDetector:
    def __init__(self, config: AppConfig) -> None:
        from ultralytics import YOLO

        self._config = config
        Path(config.model_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self._model = YOLO(config.model_path)
        names = self._model.names
        self._target_ids = {class_id for class_id, label in names.items() if label in config.target_labels}
        self._overlay_ids = [class_id for class_id, label in names.items() if label in config.overlay_labels]
        if not self._target_ids:
            targets = ", ".join(sorted(config.target_labels))
            raise ValueError(f"Model does not expose any target labels matching: {targets}")

    def analyze(self, frame) -> DetectionSummary:
        import cv2

        result = self._model(frame, verbose=False, classes=self._overlay_ids)[0]
        annotated = result.plot(conf=False)
        frame_height, frame_width = frame.shape[:2]
        frame_area = float(frame_height * frame_width)

        target_count = 0
        if result.boxes is not None and len(result.boxes) > 0:
            for class_id, confidence, xyxy in zip(
                result.boxes.cls.tolist(),
                result.boxes.conf.tolist(),
                result.boxes.xyxy.tolist(),
            ):
                if class_id not in self._target_ids:
                    continue
                if confidence < self._config.confidence_threshold:
                    continue

                x1, y1, x2, y2 = xyxy
                box_area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
                if frame_area == 0 or (box_area / frame_area) < self._config.min_box_area_ratio:
                    continue
                target_count += 1

        if target_count:
            cv2.rectangle(annotated, (0, 0), (frame_width - 1, frame_height - 1), (0, 0, 255), 5)

        return DetectionSummary(
            annotated_frame=annotated,
            target_visible=target_count > 0,
            target_count=target_count,
        )
