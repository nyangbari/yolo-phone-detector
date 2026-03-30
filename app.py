from __future__ import annotations

import time

from config import AppConfig, parse_args
from detector import PhoneDetector
from events import AlertGate, DetectionHistory
from ui import DashboardRenderer


class PhoneDetectorApp:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._detector = PhoneDetector(config)
        self._gate = AlertGate(config)
        self._history = DetectionHistory(config.history_limit)
        self._dashboard = DashboardRenderer(
            config.panel_width,
            config.target_labels,
        )

    def run(self) -> int:
        import cv2

        capture = self._open_camera()
        print("ℹ️ Focus Guard is live. Press 'q' in the detector window to quit.")
        try:
            while True:
                ok, frame = capture.read()
                if not ok:
                    print("⚠️ Camera frame read failed, stopping.")
                    break

                summary = self._detector.analyze(frame)
                triggered = self._gate.update(summary.target_visible)
                if triggered:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    self._history.record(timestamp)
                    print(f"🚨📱 {timestamp} | Phone detected")

                cooldown_ready = self._cooldown_ready()
                composed = self._dashboard.compose(
                    summary.annotated_frame,
                    self._history.entries(),
                    summary.target_count,
                    cooldown_ready,
                )
                cv2.imshow(self._config.window_name, composed)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            capture.release()
            cv2.destroyAllWindows()
        return 0

    def _open_camera(self):
        import cv2

        capture = None
        for attempt in range(1, self._config.camera_retries + 1):
            candidate = self._open_capture_candidate(cv2)
            if candidate.isOpened():
                capture = candidate
                break
            print(f"⚠️ Camera open failed ({attempt}/{self._config.camera_retries}), retrying...")
            candidate.release()
            time.sleep(1)

        if capture is None or not capture.isOpened():
            raise RuntimeError("Could not open webcam.")

        try:
            capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
        return capture

    def _open_capture_candidate(self, cv2):
        if self._config.camera_mode == "csi":
            pipeline = self._build_jetson_csi_pipeline()
            return cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        return cv2.VideoCapture(self._config.camera_index)

    def _build_jetson_csi_pipeline(self) -> str:
        return (
            "nvarguscamerasrc "
            f"sensor-id={self._config.camera_sensor_id} ! "
            f"video/x-raw(memory:NVMM), width={self._config.camera_width}, height={self._config.camera_height}, "
            f"format=NV12, framerate={self._config.camera_fps}/1 ! "
            f"nvvidconv flip-method={self._config.camera_flip_method} ! "
            "video/x-raw, format=BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=BGR ! "
            "appsink drop=true max-buffers=1"
        )

    def _cooldown_ready(self) -> bool:
        return self._gate.cooldown_ready()


def main() -> int:
    return PhoneDetectorApp(parse_args()).run()


if __name__ == "__main__":
    raise SystemExit(main())
