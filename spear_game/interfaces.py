# spear_game/interfaces.py

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class IAudio(Protocol):
    """Audio abstraction to decouple game logic from the concrete mixer."""
    # Basic state
    is_muted: bool
    music_volume: float
    sfx_volume: float

    # Settings persistence
    def load_settings(self) -> None: ...
    def save_settings(self) -> None: ...
    def apply_all_volumes(self) -> None: ...

    # Runtime controls
    def play_music(self, track_key: str, loops: int = -1, fade_ms: int = 1000) -> None: ...
    def stop_music(self, fade_ms: int = 1000) -> None: ...
    def play_sfx(self, sfx_key: str, fallback_key: str | None = None, ignore_errors: bool = False) -> None: ...
    def set_music_volume(self, volume: float) -> None: ...
    def set_sfx_volume(self, volume: float) -> None: ...
    def toggle_mute(self) -> None: ...


class IState(ABC):
    """Minimal state interface for the state machine."""

    @abstractmethod
    def handle_events(self, events) -> None: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def draw(self, screen) -> None: ...

    # Optional lifecycle hooks
    def on_enter(self) -> None:  # noqa: D401
        """Called when the state becomes current."""
        pass

    def on_exit(self) -> None:  # noqa: D401
        """Called when the state is replaced by another."""
        pass

    def on_pause(self) -> None:  # noqa: D401
        """Called when another state is temporarily placed on top (e.g., pause)."""
        pass

    def on_resume(self) -> None:  # noqa: D401
        """Called when the state becomes active again after a pause."""
        pass
