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
            candidate = cv2.VideoCapture(self._config.camera_index)
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

    def _cooldown_ready(self) -> bool:
        return self._gate.cooldown_ready()


def main() -> int:
    return PhoneDetectorApp(parse_args()).run()


if __name__ == "__main__":
    raise SystemExit(main())
