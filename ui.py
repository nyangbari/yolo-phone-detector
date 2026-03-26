from __future__ import annotations


class DashboardRenderer:
    def __init__(self, panel_width: int, target_labels: set[str]) -> None:
        self._panel_width = panel_width
        self._target_label = self._format_target_labels(target_labels)

    def compose(
        self,
        frame,
        history: list[str],
        target_count: int,
        cooldown_ready: bool,
    ):
        import cv2
        import numpy as np

        panel = np.full((frame.shape[0], self._panel_width, 3), (18, 21, 27), dtype=np.uint8)
        cv2.rectangle(panel, (0, 0), (self._panel_width - 1, frame.shape[0] - 1), (52, 58, 70), 1)
        cv2.rectangle(panel, (0, 0), (8, frame.shape[0] - 1), (0, 90, 255), -1)

        self._draw_header(panel, target_count, cooldown_ready)
        self._draw_history(panel, history)
        self._draw_footer(panel)
        return np.hstack([frame, panel])

    def _draw_header(self, panel, target_count: int, cooldown_ready: bool) -> None:
        import cv2

        card_top = 18
        card_bottom = 104
        cv2.rectangle(panel, (20, card_top), (self._panel_width - 18, card_bottom), (28, 33, 42), -1)
        cv2.rectangle(panel, (20, card_top), (self._panel_width - 18, card_bottom), (62, 70, 84), 1)

        count_color = (0, 90, 255) if target_count else (132, 142, 158)
        cv2.putText(panel, "FOCUS GUARD", (30, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (188, 197, 210), 2)
        cv2.putText(panel, str(target_count), (30, 88), cv2.FONT_HERSHEY_DUPLEX, 1.5, count_color, 3)
        cv2.putText(panel, self._pluralize("phone", target_count) + " in view", (92, 66), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (236, 239, 244), 2)
        cv2.putText(panel, f"Watching: {self._target_label}", (92, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (140, 152, 170), 1)

        self._draw_status_pill(
            panel,
            "ARMED" if cooldown_ready else "COOLDOWN",
            self._panel_width - 138,
            28,
            (72, 155, 96) if cooldown_ready else (0, 140, 220),
        )

    def _draw_history(self, panel, history: list[str]) -> None:
        import cv2

        cv2.putText(panel, "Alert Timeline", (20, 136), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (218, 222, 228), 2)
        y = 166
        if not history:
            self._draw_empty_state(panel, y)
            return

        for entry in reversed(history):
            card_top = y - 18
            card_bottom = y + 34
            if card_bottom > panel.shape[0] - 60:
                break

            cv2.rectangle(panel, (20, card_top), (self._panel_width - 18, card_bottom), (24, 28, 35), -1)
            cv2.rectangle(panel, (20, card_top), (self._panel_width - 18, card_bottom), (49, 56, 67), 1)
            cv2.putText(panel, entry, (34, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (148, 159, 176), 1)
            self._draw_alert_badge(panel, 38, y + 18)
            cv2.putText(panel, "Phone detected", (56, y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.56, (0, 90, 255), 2)
            y += 62

    def _draw_empty_state(self, panel, y: int) -> None:
        import cv2

        card_top = y - 18
        card_bottom = y + 34
        cv2.rectangle(panel, (20, card_top), (self._panel_width - 18, card_bottom), (24, 28, 35), -1)
        cv2.rectangle(panel, (20, card_top), (self._panel_width - 18, card_bottom), (49, 56, 67), 1)
        cv2.circle(panel, (38, y + 18), 8, (72, 155, 96), -1)
        cv2.putText(panel, "Watching for phone activity", (56, y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (164, 173, 186), 1)

    def _draw_footer(self, panel) -> None:
        import cv2

        footer_y = panel.shape[0] - 38
        cv2.line(panel, (20, footer_y - 16), (self._panel_width - 20, footer_y - 16), (49, 56, 67), 1)
        cv2.putText(panel, f"Target: {self._target_label}", (20, footer_y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (158, 168, 181), 1)
        cv2.putText(panel, "Press Q to quit", (self._panel_width - 132, footer_y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (158, 168, 181), 1)

    def _draw_status_pill(self, panel, text: str, x: int, y: int, color: tuple[int, int, int]) -> None:
        import cv2

        width = 108
        height = 28
        cv2.rectangle(panel, (x, y), (x + width, y + height), color, -1)
        cv2.putText(panel, text, (x + 14, y + 19), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 2)

    def _draw_alert_badge(self, panel, x: int, y: int) -> None:
        import cv2

        cv2.circle(panel, (x, y), 10, (210, 210, 210), 1)
        cv2.circle(panel, (x, y), 8, (0, 70, 255), -1)
        cv2.line(panel, (x, y - 4), (x, y + 2), (255, 255, 255), 2)
        cv2.circle(panel, (x, y + 5), 1, (255, 255, 255), -1)

    def _format_target_labels(self, target_labels: set[str]) -> str:
        ordered = sorted(label.replace("_", " ").title() for label in target_labels)
        return ", ".join(ordered)

    def _pluralize(self, word: str, count: int) -> str:
        return word if count == 1 else f"{word}s"
