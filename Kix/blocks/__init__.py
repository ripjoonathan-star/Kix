"""Definições de blocos: core (M1) + categorias (M2, M2.5, M5)."""

from Kix.blocks.builtin import (
    ALL,
    AUDIO_ADV,
    BUILTINS,
    CONTROL,
    CORE,
    FORMULA_BLOCKS,
    GESTURES_BLOCKS,
    HARDWARE_BLOCKS,
    IO,
    MATH_BLOCKS,
    MOVE,
    NETWORK,
    NOTIFICATIONS,
    PARTICLES,
    PHYSICS,
    RUNTIME,
    SAY,
    SCENES,
    SENSORS,
    STORAGE_BLOCKS,
    STRINGS,
    TRANSFORMS,
    UI_BLOCKS,
    VISUAL,
    WAIT,
    WORLD,
    AI,
    ARVR,
)
from Kix.blocks.layer import LAYERS
from Kix.blocks.event import EVENTS

__all__ = [
    "BUILTINS", "ALL", "CORE",
    "MOVE", "SAY", "WAIT", "COMPUTE",
    "TRANSFORMS", "VISUAL", "RUNTIME", "CONTROL",
    "IO", "NETWORK", "WORLD", "UI_BLOCKS",
    "MATH_BLOCKS", "STRINGS", "PHYSICS", "PARTICLES",
    "AUDIO_ADV", "SCENES", "AI", "STORAGE_BLOCKS",
    "NOTIFICATIONS", "ARVR",
    "FORMULA_BLOCKS", "SENSORS", "HARDWARE_BLOCKS", "GESTURES_BLOCKS",
    "LAYERS", "EVENTS",
]