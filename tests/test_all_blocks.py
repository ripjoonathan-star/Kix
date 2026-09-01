"""Testes para os 168 blocos distribuídos por categoria."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from Kix.block_engine import KixBlock
from Kix.blocks import (
    ALL,
    AI,
    AUDIO_ADV,
    CONTROL,
    EVENTS,
    FORMULA_BLOCKS,
    GESTURES_BLOCKS,
    HARDWARE_BLOCKS,
    IO,
    LAYERS,
    MATH_BLOCKS,
    NETWORK,
    NOTIFICATIONS,
    PARTICLES,
    PHYSICS,
    RUNTIME,
    SCENES,
    SENSORS,
    STORAGE_BLOCKS,
    STRINGS,
    TRANSFORMS,
    UI_BLOCKS,
    VISUAL,
    WORLD,
    ARVR,
)
from Kix.blocks.builtin import BUILTINS, CORE


# --- Smoke: contagem por categoria ----------------------------------------
EXPECTED = {
    "CORE": (CORE, 4),
    "TRANSFORMS": (TRANSFORMS, 35),
    "VISUAL": (VISUAL, 36),
    "RUNTIME": (RUNTIME, 29),
    "CONTROL": (CONTROL, 15),
    "IO": (IO, 25),
    "NETWORK": (NETWORK, 17),
    "WORLD": (WORLD, 26),
    "UI_BLOCKS": (UI_BLOCKS, 10),
    "MATH_BLOCKS": (MATH_BLOCKS, 23),
    "STRINGS": (STRINGS, 8),
    "PHYSICS": (PHYSICS, 12),
    "PARTICLES": (PARTICLES, 8),
    "AUDIO_ADV": (AUDIO_ADV, 8),
    "FORMULA_BLOCKS": (FORMULA_BLOCKS, 20),  # 7 arith + 1 neg + 6 cmp + 4 logic + 4 str = 20
    "SENSORS": (SENSORS, 18),
    "HARDWARE_BLOCKS": (HARDWARE_BLOCKS, 16),  # 8 nxt + 6 arduino + 2 makey
    "GESTURES_BLOCKS": (GESTURES_BLOCKS, 15),  # 6 touch + 1 pen + 5 data + 2 physics + 1 event
    "STORAGE_BLOCKS": (STORAGE_BLOCKS, 11),
    "SCENES": (SCENES, 4),
    "AI": (AI, 6),
    "NOTIFICATIONS": (NOTIFICATIONS, 3),
    "ARVR": (ARVR, 3),
    "LAYERS": (LAYERS, 19),  # 19 layer blocks (criar/remover/reordenar/visibility/colisão/shader/...)
    "EVENTS": (EVENTS, 11),  # 8 hat-blocks + 3 broadcast (Pocket Code event blocks)
}


@pytest.mark.parametrize("name", list(EXPECTED.keys()))
def test_category_count(name):
    blocks, expected = EXPECTED[name]
    assert len(blocks) == expected, (
        f"{name}: esperado {expected}, obtido {len(blocks)}"
    )


def test_total_at_least_150():
    total = sum(len(blocks) for blocks, _ in EXPECTED.values())
    assert total >= 150, f"Total {total} abaixo de 150"
    # Sanity: bate com ALL
    assert len(ALL) == total, f"ALL ({len(ALL)}) != soma das categorias ({total})"


def test_total_at_least_186():
    """M3.3: cobertura Catroid adiciona ~37 blocos; total agora ≥186."""
    total = sum(len(blocks) for blocks, _ in EXPECTED.values())
    assert total >= 186, f"Total {total} abaixo de 186 (esperado pós-M3.3)"


# --- IDs únicos em ALL ----------------------------------------------------
def test_all_ids_unique():
    ids = [b.id for b in ALL]
    assert len(ids) == len(set(ids)), f"IDs duplicados: {sorted(set([i for i in ids if ids.count(i) > 1]))}"


def test_bultins_unchanged_ids():
    """Blocos core.* devem manter seus IDs originais para compat."""
    ids = {b.id for b in BUILTINS}
    assert ids == {"core.move", "core.say", "core.wait", "core.compute"}


# --- Todos os blocos instanciam e fazem round-trip -----------------------
def test_every_block_round_trips():
    for b in ALL:
        assert isinstance(b, KixBlock)
        data = b.to_dict()
        back = KixBlock.from_dict(data)
        assert back.id == b.id
        assert back.name == b.name
        assert back.color == b.color
        assert len(back.inputs) == len(b.inputs)
        assert len(back.outputs) == len(b.outputs)
        assert back.permissions == b.permissions


# --- Categorias válidas ----------------------------------------------------
VALID_CATEGORIES = {
    "motion", "looks", "sound", "pen", "control", "event", "data",
    "sensing", "device", "files", "user", "libs", "camera", "network",
    "layers", "shaders", "ui", "tilemap", "spritesheet", "joystick", "math",
    "strings", "physics", "particles", "audio_advanced", "scenes", "ai",
    "storage", "notifications", "arvr",
}


def test_every_block_has_valid_category():
    invalid = [(b.id, b.category) for b in ALL if b.category not in VALID_CATEGORIES]
    assert not invalid, f"Categorias inválidas: {invalid}"


# --- Permissions são set --------------------------------------------------
def test_every_block_has_permissions_set():
    """Blocos sem permissions podem quebrar o controle de segurança."""
    no_perms = [b.id for b in ALL if b.permissions is None]
    assert not no_perms, f"Blocos sem permissions (None): {no_perms}"


# --- Visual não é None para nenhum bloco ---------------------------------
def test_every_block_has_visual():
    no_visual = [b.id for b in ALL if b.visual is None]
    assert not no_visual, f"Blocos sem visual: {no_visual}"


# --- Behavior: deve ter language válida quando não-None -------------------
def test_every_behavior_has_valid_language():
    from Kix.block_engine.behavior import BlockBehavior

    invalid = []
    for b in ALL:
        bh = b.behavior
        if bh is None:
            continue
        if not isinstance(bh, BlockBehavior):
            invalid.append(b.id)
            continue
        if bh.language not in {"python", "lua"}:
            invalid.append(b.id)
    assert not invalid, f"Behavior inválido em: {invalid}"


# --- Cores por categoria ---------------------------------------------------
def test_category_colors_distinct():
    """Cada categoria deve ter um tom diferente para distinguir visualmente."""
    from Kix.core.theme import (
        CAT_CAMERA, CAT_CONTROL, CAT_DATA, CAT_DEVICE, CAT_FILES,
        CAT_JOYSTICK, CAT_LAYERS, CAT_LIBS, CAT_LOOKS, CAT_MOTION,
        CAT_NETWORK, CAT_PEN, CAT_SHADERS, CAT_SOUND, CAT_SPRITESHEET,
        CAT_TILEMAP, CAT_UI, CAT_USER,
    )
    palette = [CAT_CAMERA, CAT_CONTROL, CAT_DATA, CAT_DEVICE, CAT_FILES,
               CAT_JOYSTICK, CAT_LAYERS, CAT_LIBS, CAT_LOOKS, CAT_MOTION,
               CAT_NETWORK, CAT_PEN, CAT_SHADERS, CAT_SOUND, CAT_SPRITESHEET,
               CAT_TILEMAP, CAT_UI, CAT_USER]
    assert len(palette) == len(set(palette)), "Há cores duplicadas no tema"