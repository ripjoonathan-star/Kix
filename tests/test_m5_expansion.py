"""M5: testes para o lote Catroid (fórmula, sensors, hardware, gestos/dados)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from Kix.blocks.formula import FORMULA_BLOCKS, ARITH_BLOCKS, CMP_BLOCKS, LOGIC_BLOCKS, STR_OPS
from Kix.blocks.sensors import SENSORS
from Kix.blocks.hardware import HARDWARE_BLOCKS, LEGO_BLOCKS, ARDUINO_BLOCKS, MAKEY_BLOCKS
from Kix.blocks.gestures import GESTURES_BLOCKS, TOUCH_BLOCKS, PEN_BLOCKS, DATA_BLOCKS, PHYSICS_BLOCKS, EVENT_BLOCKS
from Kix.engine.ctx import make_ctx
from Kix.engine.executor import BlockExecutor


def _find(blocks, id_):
    for b in blocks:
        if b.id == id_:
            return b
    raise KeyError(id_)


async def _run(block, ctx=None, **inputs):
    if ctx is None:
        ctx = make_ctx()
    return await BlockExecutor().run_block(block, ctx, inputs)


# ---------- Fórmula: aritmética ------------------------------------------
@pytest.mark.parametrize("block", [b for b in ARITH_BLOCKS if b.id != "math.op.neg"], ids=lambda b: b.id)
async def test_arith_block_runs(block):
    out = await _run(block, a=10, b=3)
    assert isinstance(out, (int, float))


async def test_neg_block_runs():
    block = _find(ARITH_BLOCKS, "math.op.neg")
    out = await _run(block, n=42)
    assert out == -42


async def test_add_returns_sum():
    block = _find(ARITH_BLOCKS, "math.op.add")
    assert await _run(block, a=4, b=7) == 11


async def test_div_returns_zero_on_zero_divisor():
    block = _find(ARITH_BLOCKS, "math.op.div")
    assert await _run(block, a=10, b=0) == 0


async def test_pow_returns_power():
    block = _find(ARITH_BLOCKS, "math.op.pow")
    assert await _run(block, a=2, b=10) == 1024


async def test_neg_returns_negative():
    block = _find(ARITH_BLOCKS, "math.op.neg")
    assert await _run(block, n=42) == -42


# ---------- Fórmula: comparação -------------------------------------------
async def test_eq_returns_true_when_equal():
    block = _find(CMP_BLOCKS, "math.cmp.eq")
    assert await _run(block, a=5, b=5) is True


async def test_ne_returns_true_when_different():
    block = _find(CMP_BLOCKS, "math.cmp.ne")
    assert await _run(block, a=5, b=6) is True


# ---------- Fórmula: lógica -----------------------------------------------
async def test_and_truth_table():
    block = _find(LOGIC_BLOCKS, "logic.and")
    assert (await _run(block, a=True, b=True)) is True
    assert (await _run(block, a=True, b=False)) is False
    assert (await _run(block, a=False, b=True)) is False
    assert (await _run(block, a=False, b=False)) is False


async def test_not_inverts():
    block = _find(LOGIC_BLOCKS, "logic.not")
    assert (await _run(block, a=True)) is False
    assert (await _run(block, a=False)) is True


# ---------- Sensores -----------------------------------------------------
async def test_gps_lat_returns_default():
    block = _find(SENSORS, "sensing.gps_lat")
    assert await _run(block) == 0.0


async def test_compass_returns_default():
    block = _find(SENSORS, "sensing.compass")
    assert await _run(block) == 0.0


async def test_tilt_x_returns_configured():
    block = _find(SENSORS, "sensing.tilt_x")
    ctx = make_ctx()
    ctx.services.device.tilt = (0.42, 0.0)
    assert await _run(block, ctx=ctx) == 0.42


async def test_nfc_returns_empty_string_when_unread():
    block = _find(SENSORS, "sensing.nfc_last_tag")
    assert await _run(block) == ""


async def test_nfc_has_read_false_when_unread():
    block = _find(SENSORS, "sensing.nfc_has_read")
    assert (await _run(block)) is False


# ---------- Hardware (Lego NXT) -------------------------------------------
async def test_nxt_connect_records_address():
    block = _find(HARDWARE_BLOCKS, "lego.nxt.connect")
    ctx = make_ctx()
    await _run(block, ctx=ctx, address="AA:BB:CC:DD:EE:FF")
    assert ctx.services.nxt.connected is True
    assert ctx.services.nxt.address == "AA:BB:CC:DD:EE:FF"


async def test_nxt_motor_records_call():
    block = _find(HARDWARE_BLOCKS, "lego.nxt.motor")
    ctx = make_ctx()
    await _run(block, ctx=ctx, port="A", speed=75, duration=2.0)
    assert ctx.services.nxt._attrs["last_motor"] == ("A", 75.0, 2.0)


async def test_arduino_digital_write_records_pin():
    block = _find(HARDWARE_BLOCKS, "arduino.digital_write")
    ctx = make_ctx()
    await _run(block, ctx=ctx, pin=13, value=True)
    assert ctx.services.arduino._attrs["d_13"] is True


async def test_arduino_analog_read_returns_zero_initially():
    block = _find(HARDWARE_BLOCKS, "arduino.analog_read")
    assert await _run(block, pin=0) == 0


# ---------- Gestos / touch -----------------------------------------------
async def test_touch_last_xy_default():
    block_x = _find(TOUCH_BLOCKS, "touch.last_x")
    block_y = _find(TOUCH_BLOCKS, "touch.last_y")
    ctx = make_ctx()
    assert await _run(block_x, ctx=ctx) == 0.0
    assert await _run(block_y, ctx=ctx) == 0.0


async def test_touch_feed_records_position():
    ctx = make_ctx()
    ctx.services.touch.feed_touch(100, 200)
    assert ctx.services.touch.last_x == 100
    assert ctx.services.touch.last_y == 200
    assert ctx.services.touch.is_touched is True


async def test_shake_triggers_on_high_accel():
    block = _find(TOUCH_BLOCKS, "touch.shake")
    ctx = make_ctx()
    ctx.services.device.accel = (2.0, 0.0, 0.0)  # magnitude ~2.0 → abaixo
    assert (await _run(block, ctx=ctx)) is False
    ctx.services.device.accel = (3.0, 0.0, 0.0)  # magnitude 3.0 → acima
    assert (await _run(block, ctx=ctx)) is True


# ---------- Dados: variáveis custom ---------------------------------------
async def test_var_declare_then_get():
    declare = _find(DATA_BLOCKS, "data.declare_variable")
    get = _find(DATA_BLOCKS, "data.get_variable")
    ctx = make_ctx()
    await _run(declare, ctx=ctx, name="hp", value=42)
    assert await _run(get, ctx=ctx, name="hp", default=0) == 42


async def test_var_get_returns_default_when_missing():
    block = _find(DATA_BLOCKS, "data.get_variable")
    assert await _run(block, name="does_not_exist", default=99) == 99


async def test_var_delete_removes():
    declare = _find(DATA_BLOCKS, "data.declare_variable")
    delete = _find(DATA_BLOCKS, "data.delete_variable")
    get = _find(DATA_BLOCKS, "data.get_variable")
    ctx = make_ctx()
    await _run(declare, ctx=ctx, name="tmp", value=1)
    await _run(delete, ctx=ctx, name="tmp")
    assert "tmp" not in ctx.variables
    # e get retorna default
    assert await _run(get, ctx=ctx, name="tmp", default=0) == 0


# ---------- Listas ---------------------------------------------------------
async def test_list_declare_then_get():
    declare = _find(DATA_BLOCKS, "data.declare_list")
    get = _find(DATA_BLOCKS, "data.list_get")
    ctx = make_ctx()
    await _run(declare, ctx=ctx, name="items", initial=3)
    assert ctx.variables["items"] == [0, 1, 2]
    # 1-based: index=2 → items[1] = 1
    assert await _run(get, ctx=ctx, name="items", index=2) == 1


# ---------- Storage (M5 expandido) -----------------------------------------
async def test_storage_set_and_get_number():
    from Kix.blocks.storage import STORAGE_SET_NUMBER, STORAGE_GET_NUMBER
    ctx = make_ctx()
    await _run(STORAGE_SET_NUMBER, ctx=ctx, key="score", value=42)
    assert await _run(STORAGE_GET_NUMBER, ctx=ctx, key="score", default=0) == 42


async def test_storage_size_after_set():
    from Kix.blocks.storage import STORAGE_SET, STORAGE_SIZE
    ctx = make_ctx()
    assert await _run(STORAGE_SIZE, ctx=ctx) == 0
    await _run(STORAGE_SET, ctx=ctx, key="a", value="x")
    await _run(STORAGE_SET, ctx=ctx, key="b", value="y")
    assert await _run(STORAGE_SIZE, ctx=ctx) == 2


# ---------- Controle: scripts aninhados (M5) -------------------------------
async def test_repeat_runs_body_n_times():
    """`control.repeat` executa body N vezes."""
    from Kix.blocks.control import REPEAT
    from Kix.blocks.builtin import MOVE

    ctx = make_ctx()
    body = [MOVE.to_dict()]
    sprite = ctx.stage.active
    sprite.position = (0, 0)

    inputs = {"times": 3, "body": body}
    await _run(REPEAT, ctx=ctx, **inputs)
    # MOVE.steps default = 10 → 3 × 10 = 30
    assert sprite.position == (30, 0)


async def test_forever_source_compiles_and_loops():
    """`control.forever` deve ter source válida que compila e tem `while True`."""
    from Kix.blocks.control import FOREVER
    assert FOREVER.behavior is not None
    assert "while True" in FOREVER.behavior.source
    # O loop infinito é intencional — verificamos apenas que compila
    from Kix.engine.executor import compile_source_to_code
    code = compile_source_to_code(FOREVER.behavior.source)
    assert code is not None


async def test_repeat_zero_times_is_noop():
    """`control.repeat` com 0 não executa o body."""
    from Kix.blocks.control import REPEAT
    from Kix.blocks.builtin import MOVE

    ctx = make_ctx()
    body = [MOVE.to_dict()]
    sprite = ctx.stage.active
    start_x = sprite.position[0]
    await _run(REPEAT, ctx=ctx, times=0, body=body)
    assert sprite.position[0] == start_x


async def test_if_runs_body_only_when_true():
    """`control.if` deve executar body apenas quando condition é truthy."""
    from Kix.blocks.control import IF
    from Kix.blocks.builtin import MOVE

    ctx = make_ctx()
    body = [MOVE.to_dict()]
    sprite = ctx.stage.active
    start_x = sprite.position[0]

    # condition False → não move
    await _run(IF, ctx=ctx, condition=False, body=body)
    assert sprite.position[0] == start_x

    # condition True → move
    await _run(IF, ctx=ctx, condition=True, body=body)
    assert sprite.position[0] == start_x + 10


# ---------- Categorias presentes em ALL ------------------------------------
def test_new_categories_present_in_all():
    from Kix.blocks.builtin import ALL
    ids = {b.id for b in ALL}
    must_have = {
        "math.op.add", "math.op.sub", "math.cmp.eq", "logic.and", "logic.not",
        "sensing.gps_lat", "sensing.compass", "sensing.tilt_x",
        "lego.nxt.connect", "arduino.digital_write",
        "makey.is_pressed",
        "touch.last_x", "data.declare_variable", "physics.gravity",
        "control.when_receive",
    }
    missing = must_have - ids
    assert not missing, f"Blocos M5 ausentes em ALL: {missing}"
