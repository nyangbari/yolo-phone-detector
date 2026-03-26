from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass

from config import AppConfig


@dataclass(slots=True)
class TriggerState:
    streak: int = 0
    last_trigger_at: float = 0.0


class DetectionHistory:
    def __init__(self, limit: int) -> None:
        self._entries: deque[str] = deque(maxlen=limit)

    def record(self, timestamp: str) -> None:
        self._entries.append(timestamp)

    def entries(self) -> list[str]:
        return list(self._entries)


class AlertGate:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._state = TriggerState()

    def update(self, detected: bool, now: float | None = None) -> bool:
        current_time = time.time() if now is None else now
        if detected:
            self._state.streak += 1
        else:
            self._state.streak = 0
            return False

        ready = self._state.streak >= self._config.streak_required
        cooled_down = (current_time - self._state.last_trigger_at) >= self._config.cooldown_seconds
        if not (ready and cooled_down):
            return False

        self._state.last_trigger_at = current_time
        self._state.streak = 0
        return True

    @property
    def streak(self) -> int:
        return self._state.streak

    def cooldown_ready(self, now: float | None = None) -> bool:
        current_time = time.time() if now is None else now
        return (current_time - self._state.last_trigger_at) >= self._config.cooldown_seconds
