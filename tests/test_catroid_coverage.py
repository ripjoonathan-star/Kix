"""Smoke tests para os 37 blocos adicionados na cobertura Catroid (M3.3).

Cobre:
- math: ln, log10, pi, atan, mod, round_to
- looks property reporters: object_name, object_rotation, opacity,
  brightness, tint, look_index, look_name, look_width, look_height,
  look_count
- motion property reporters: position_x, position_y, size, width,
  height, direction
- sensing: screen_width, screen_height, fps, color_at, color_equal_tolerance
- device: accel_y, accel_z, clipboard_text, keyboard_height
- platform: architecture
- network: is_connected, local_ip, local_port
- audio: volume_reporter, mic.frequency
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from Kix.blocks import ALL
from Kix.blocks.math_blocks import MATH_BLOCKS
from Kix.blocks.visual import VISUAL
from Kix.blocks.transforms import TRANSFORMS
from Kix.blocks.runtime import RUNTIME
from Kix.blocks.io import IO
from Kix.blocks.network import NETWORK
from Kix.blocks.audio_advanced import AUDIO_ADV
from Kix.engine.ctx import make_ctx
from Kix.engine.executor import BlockExecutor


def _find(blocks, id_: str):
    for b in blocks:
        if b.id == id_:
            return b
    raise KeyError(f"Bloco {id_!r} não encontrado em {len(blocks)} blocos")


async def _run(block, ctx=None, **inputs):
    if ctx is None:
        ctx = make_ctx()
    return await BlockExecutor().run_block(block, ctx, inputs)


# ---------- math via decorator --------------------------------------------
async def test_math_ln_returns_natural_log():
    block = _find(MATH_BLOCKS, "math.ln")
    out = await _run(block, n=math.e)
    assert abs(out - 1.0) < 1e-9


async def test_math_log10_returns_log10():
    block = _find(MATH_BLOCKS, "math.log10")
    out = await _run(block, n=1000)
    assert abs(out - 3.0) < 1e-9


async def test_math_pi_returns_pi():
    block = _find(MATH_BLOCKS, "math.pi")
    out = await _run(block)
    assert abs(out - math.pi) < 1e-9


async def test_math_atan_single_arg():
    block = _find(MATH_BLOCKS, "math.atan")
    out = await _run(block, n=1)
    assert abs(out - 45.0) < 1e-9


async def test_math_mod_basic():
    block = _find(MATH_BLOCKS, "math.mod")
    out = await _run(block, a=10, b=3)
    assert out == 1


async def test_math_round_to_two_decimals():
    block = _find(MATH_BLOCKS, "math.round_to")
    out = await _run(block, n=3.14159, decimals=2)
    assert abs(out - 3.14) < 1e-9


# ---------- looks property reporters --------------------------------------
async def test_object_name_returns_sprite_name():
    block = _find(VISUAL, "looks.object_name")
    ctx = make_ctx()
    ctx.stage.active.name = "Player1"
    out = await _run(block, ctx=ctx)
    assert out == "Player1"


async def test_object_rotation_returns_sprite_rotation():
    block = _find(VISUAL, "looks.object_rotation")
    ctx = make_ctx()
    ctx.stage.active.rotation = 42.5
    out = await _run(block, ctx=ctx)
    assert out == 42.5


async def test_object_opacity_returns_sprite_opacity():
    block = _find(VISUAL, "looks.object_opacity")
    ctx = make_ctx()
    ctx.stage.active.opacity = 0.7
    out = await _run(block, ctx=ctx)
    assert out == 0.7


async def test_object_brightness_returns_sprite_brightness():
    block = _find(VISUAL, "looks.object_brightness")
    ctx = make_ctx()
    ctx.stage.active.brightness = 1.5
    out = await _run(block, ctx=ctx)
    assert out == 1.5


async def test_object_tint_returns_sprite_tint():
    block = _find(VISUAL, "looks.object_tint")
    ctx = make_ctx()
    ctx.stage.active.tint = (0.1, 0.2, 0.3, 1.0)
    out = await _run(block, ctx=ctx)
    assert out == (0.1, 0.2, 0.3, 1.0)


async def test_look_index_returns_frame_index():
    block = _find(VISUAL, "looks.look_index")
    ctx = make_ctx()
    ctx.stage.active.frame_index = 7
    out = await _run(block, ctx=ctx)
    assert out == 7


async def test_look_name_returns_animation_name():
    block = _find(VISUAL, "looks.look_name")
    ctx = make_ctx()
    ctx.stage.active.current_animation = "walk"
    out = await _run(block, ctx=ctx)
    assert out == "walk"


async def test_look_width_returns_fw():
    block = _find(VISUAL, "looks.look_width")
    ctx = make_ctx()
    ctx.stage.active.fw = 128.0
    out = await _run(block, ctx=ctx)
    assert out == 128.0


async def test_look_height_returns_fh():
    block = _find(VISUAL, "looks.look_height")
    ctx = make_ctx()
    ctx.stage.active.fh = 64.0
    out = await _run(block, ctx=ctx)
    assert out == 64.0


async def test_look_count_returns_count():
    block = _find(VISUAL, "looks.look_count")
    ctx = make_ctx()
    ctx.stage.active.count = 5
    out = await _run(block, ctx=ctx)
    assert out == 5


# ---------- motion property reporters -------------------------------------
async def test_motion_position_x_returns_x():
    block = _find(TRANSFORMS, "motion.position_x")
    ctx = make_ctx()
    ctx.stage.active.position = (42, 7)
    out = await _run(block, ctx=ctx)
    assert out == 42


async def test_motion_position_y_returns_y():
    block = _find(TRANSFORMS, "motion.position_y")
    ctx = make_ctx()
    ctx.stage.active.position = (42, 7)
    out = await _run(block, ctx=ctx)
    assert out == 7


async def test_motion_size_returns_size():
    block = _find(TRANSFORMS, "motion.size")
    ctx = make_ctx()
    ctx.stage.active.size = 80.0
    out = await _run(block, ctx=ctx)
    assert out == 80.0


async def test_motion_width_returns_fw():
    block = _find(TRANSFORMS, "motion.width")
    ctx = make_ctx()
    ctx.stage.active.fw = 100.0
    out = await _run(block, ctx=ctx)
    assert out == 100.0


async def test_motion_height_returns_fh():
    block = _find(TRANSFORMS, "motion.height")
    ctx = make_ctx()
    ctx.stage.active.fh = 200.0
    out = await _run(block, ctx=ctx)
    assert out == 200.0


async def test_motion_direction_returns_direction():
    block = _find(TRANSFORMS, "motion.direction")
    ctx = make_ctx()
    ctx.stage.active.direction = 135.0
    out = await _run(block, ctx=ctx)
    assert out == 135.0


# ---------- sensing (screen, fps, color) ----------------------------------
async def test_sensing_screen_width():
    block = _find(RUNTIME, "sensing.screen_width")
    out = await _run(block)
    assert out == 390


async def test_sensing_screen_height():
    block = _find(RUNTIME, "sensing.screen_height")
    out = await _run(block)
    assert out == 844


async def test_sensing_fps():
    block = _find(RUNTIME, "sensing.fps")
    out = await _run(block)
    assert out == 60.0


async def test_sensing_color_at_x_y():
    block = _find(RUNTIME, "sensing.color_at_x_y")
    out = await _run(block, x=10, y=20)
    assert out == "#000000"


async def test_sensing_color_equal_tolerance():
    block = _find(RUNTIME, "sensing.color_equal_tolerance")
    out = await _run(block, a="#ff0000", b="#ff0000", tolerance=0)
    assert out is True


# ---------- device (accel y/z, clipboard, keyboard) ----------------------
async def test_device_accel_y():
    block = _find(IO, "device.accel_y")
    ctx = make_ctx()
    ctx.services.device.accel = (0.1, 0.2, 0.3)
    out = await _run(block, ctx=ctx)
    assert abs(out - 0.2) < 1e-9


async def test_device_accel_z():
    block = _find(IO, "device.accel_z")
    ctx = make_ctx()
    ctx.services.device.accel = (0.1, 0.2, 0.3)
    out = await _run(block, ctx=ctx)
    assert abs(out - 0.3) < 1e-9


async def test_device_clipboard_text():
    block = _find(IO, "device.clipboard_text")
    ctx = make_ctx()
    ctx.services.device.clipboard_text = "Hello"
    out = await _run(block, ctx=ctx)
    assert out == "Hello"


async def test_device_keyboard_height():
    block = _find(IO, "device.keyboard_height")
    ctx = make_ctx()
    ctx.services.device.keyboard_height = 250.0
    out = await _run(block, ctx=ctx)
    assert out == 250.0


async def test_platform_architecture():
    block = _find(IO, "platform.architecture")
    out = await _run(block)
    assert out == "x86_64"


# ---------- network reporters ---------------------------------------------
async def test_network_is_connected():
    block = _find(NETWORK, "network.is_connected")
    ctx = make_ctx()
    ctx.services.network.is_connected = True
    out = await _run(block, ctx=ctx)
    assert out is True


async def test_network_local_ip():
    block = _find(NETWORK, "network.local_ip")
    out = await _run(block)
    assert out == "127.0.0.1"


async def test_network_local_port():
    block = _find(NETWORK, "network.local_port")
    out = await _run(block)
    assert out == 0


# ---------- audio reporters -----------------------------------------------
async def test_audio_volume_reporter():
    block = _find(AUDIO_ADV, "audio.volume_reporter")
    ctx = make_ctx()
    ctx.services.audio.volume = 0.8
    out = await _run(block, ctx=ctx)
    assert out == 0.8


async def test_audio_mic_frequency():
    block = _find(AUDIO_ADV, "audio.mic.frequency")
    ctx = make_ctx()
    ctx.services.audio.mic.frequency = 440.0
    out = await _run(block, ctx=ctx)
    assert out == 440.0


# ---------- sanity: todos os blocos novos têm source válida ---------------
def test_every_new_block_has_valid_behavior():
    """Cada bloco adicionado em M3.3 deve ter um BlockBehavior com source."""
    new_ids = {
        "math.ln", "math.log10", "math.pi", "math.atan", "math.mod", "math.round_to",
        "looks.object_name", "looks.object_rotation", "looks.object_opacity",
        "looks.object_brightness", "looks.object_tint", "looks.look_index",
        "looks.look_name", "looks.look_width", "looks.look_height", "looks.look_count",
        "motion.position_x", "motion.position_y", "motion.size",
        "motion.width", "motion.height", "motion.direction",
        "sensing.screen_width", "sensing.screen_height", "sensing.fps",
        "sensing.color_at_x_y", "sensing.color_equal_tolerance",
        "device.accel_y", "device.accel_z", "device.clipboard_text",
        "device.keyboard_height", "platform.architecture",
        "network.is_connected", "network.local_ip", "network.local_port",
        "audio.volume_reporter", "audio.mic.frequency",
    }
    found = {b.id for b in ALL}
    missing = new_ids - found
    assert not missing, f"Blocos Catroid ausentes em ALL: {missing}"
    # Cada um tem behavior (decorator-produced também conta)
    for b in ALL:
        if b.id in new_ids:
            assert b.behavior is not None, f"{b.id} sem behavior"
