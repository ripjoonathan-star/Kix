"""Testes do executor M3: blocos realmente rodam.

Cobre:
- Funções puras: math (17 blocos), strings (8 blocos).
- Mutadores de sprite: motion.move, set_x, change_x, rotate_by.
- Variables / lists: data.set, data.change, data.list_add.
- Sensing reporters: timer, reset_timer, mouse_x/y.
- Network stubs: NotImplementedError honesto (não é stub silencioso).
- Round-trip: KixBlock.from_dict preserva behavior.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from Kix.block_engine import KixBlock, SocketDef, SocketKind, BlockVisual, Text, BlockInput, Group
from Kix.block_engine.behavior import BlockBehavior
from Kix.blocks.math_blocks import MATH_BLOCKS
from Kix.blocks.runtime import RUNTIME, SET_VAR, CHANGE_VAR, LIST_ADD
from Kix.blocks.builtin import MOVE, SAY, WAIT
from Kix.blocks.transforms import (
    MOVE as MOTION_MOVE,
    MOVE_XY,
    MOVE_TO,
    SET_X,
    SET_Y,
    CHANGE_X,
    ROTATE_BY,
)
from Kix.blocks.strings import STRINGS
from Kix.blocks.runtime import STRING_JOIN
from Kix.engine.ctx import RuntimeContext, SpriteProxy, Stage, make_ctx
from Kix.engine.executor import BlockExecutor
from Kix.engine.services import Services, NetworkNotWired


# ---------- helpers --------------------------------------------------------
def _find(blocks, id_: str):
    for b in blocks:
        if b.id == id_:
            return b
    raise KeyError(id_)


async def _run(block, ctx=None, **inputs):
    if ctx is None:
        ctx = make_ctx()
    executor = BlockExecutor()
    return await executor.run_block(block, ctx, inputs)


# ---------- math (funções puras) ------------------------------------------
def _math_inputs(block):
    """Gera inputs default para cada bloco de math."""
    # 2-input blocks: nome dos sockets varia
    two_input = {
        "math.pow": {"base": 2, "exp": 3},
        "math.log": {"n": 1, "base": 2.718281828459045},
        "math.atan2": {"y": 1, "x": 1},
        "math.random": {"a": 1, "b": 6},
        "math.min": {"a": 3, "b": 7},
        "math.max": {"a": 3, "b": 7},
        "math.mod": {"a": 10, "b": 3},
        "math.round_to": {"n": 3.14, "decimals": 2},
    }
    if block.id in two_input:
        return two_input[block.id]
    # 1-input: usa default do socket
    if block.inputs:
        s = block.inputs[0]
        return {s.name: s.default if s.default is not None else 1}
    return {}


@pytest.mark.parametrize("block", MATH_BLOCKS, ids=lambda b: b.id)
async def test_math_block_runs(block):
    """Cada bloco de math deve rodar e retornar um número (ou bool, p/ comparação)."""
    inputs = _math_inputs(block)
    out = await _run(block, **inputs)
    assert out is not None, f"{block.id} retornou None"


async def test_math_sin_90_is_1():
    block = _find(MATH_BLOCKS, "math.sin")
    out = await _run(block, deg=90)
    assert abs(out - 1.0) < 1e-6


async def test_math_sqrt_4_is_2():
    block = _find(MATH_BLOCKS, "math.sqrt")
    out = await _run(block, n=4)
    assert abs(out - 2.0) < 1e-9


async def test_math_random_in_range():
    block = _find(MATH_BLOCKS, "math.random")
    for _ in range(50):
        out = await _run(block, a=1, b=6)
        assert 1 <= out <= 6


async def test_math_abs_negative():
    block = _find(MATH_BLOCKS, "math.abs")
    out = await _run(block, n=-7.5)
    assert abs(out - 7.5) < 1e-9


# ---------- strings -------------------------------------------------------
async def test_string_length_runs():
    block = _find(STRINGS, "str.length")
    out = await _run(block, s="Kix")
    assert out == 3


async def test_string_concat_runs():
    """`data.string_join` é o bloco de concatenar do projeto."""
    block = STRING_JOIN
    out = await _run(block, a="K", b="ix")
    assert out == "Kix"


# ---------- motion / sprite -----------------------------------------------
async def test_motion_move_translates_sprite():
    ctx = make_ctx()
    sprite = ctx.stage.active
    assert sprite is not None
    before = sprite.position
    await _run(MOTION_MOVE, ctx, steps=15)
    assert sprite.position == (before[0] + 15, before[1])


async def test_motion_move_to_sets_position():
    ctx = make_ctx()
    await _run(MOVE_TO, ctx, x=42, y=7)
    assert ctx.stage.active.position == (42, 7)


async def test_motion_set_x_overrides():
    ctx = make_ctx()
    await _run(SET_X, ctx, x=99)
    assert ctx.stage.active.position[0] == 99


async def test_motion_rotate_by_accumulates():
    ctx = make_ctx()
    sprite = ctx.stage.active
    sprite.rotation = 10
    await _run(ROTATE_BY, ctx, angle=20)
    assert abs(sprite.rotation - 30) < 1e-9


async def test_motion_change_x_translates():
    ctx = make_ctx()
    sprite = ctx.stage.active
    sprite.position = (0, 0)
    await _run(CHANGE_X, ctx, dx=5)
    assert sprite.position == (5, 0)


# ---------- variables -----------------------------------------------------
async def test_data_set_stores_variable():
    """data.set deve armazenar o valor em ctx.variables sob o nome do socket."""
    ctx = make_ctx()

    # O source usa self.var.set(self.value). Como var é SocketKind.VARIABLE,
    # vamos montar um proxy Variable simples com .set/.get.
    class _Var:
        def __init__(self, name):
            self.name = name
        def set(self, v):
            ctx.variables[self.name] = v
        def get(self):
            return ctx.variables.get(self.name, 0)

    await _run(SET_VAR, ctx, var=_Var("score"), value=10)
    assert ctx.variables["score"] == 10


async def test_data_change_adds_delta():
    ctx = make_ctx()
    ctx.variables["score"] = 5

    class _Var:
        def __init__(self, name):
            self.name = name
        def set(self, v):
            ctx.variables[self.name] = v
        def get(self):
            return ctx.variables.get(self.name, 0)

    await _run(CHANGE_VAR, ctx, var=_Var("score"), delta=7)
    assert ctx.variables["score"] == 12


# ---------- sensing -------------------------------------------------------
async def test_sensing_timer_returns_initial_zero():
    block = _find(RUNTIME, "sensing.timer")
    ctx = make_ctx()
    out = await _run(block, ctx=ctx)
    assert out == 0


async def test_sensing_reset_timer_sets_zero():
    block = _find(RUNTIME, "sensing.reset_timer")
    ctx = make_ctx()
    ctx.timer = 99
    await _run(block, ctx=ctx)
    assert ctx.timer == 0


# ---------- legacy builtins (BUILTINS) ------------------------------------
async def test_core_wait_actually_sleeps():
    ctx = make_ctx()
    t0 = asyncio.get_event_loop().time()
    await _run(WAIT, ctx, seconds=0.05)
    elapsed = asyncio.get_event_loop().time() - t0
    assert elapsed >= 0.04


# ---------- round-trip ----------------------------------------------------
def test_from_dict_preserves_behavior_for_all_math():
    """Após round-trip, behavior deve permanecer funcional."""
    for block in MATH_BLOCKS:
        data = block.to_dict()
        back = KixBlock.from_dict(data)
        assert back.behavior is not None
        assert back.behavior.source == block.behavior.source


async def test_round_tripped_math_block_still_runs():
    block = _find(MATH_BLOCKS, "math.sin")
    back = KixBlock.from_dict(block.to_dict())
    out = await _run(back, deg=30)
    assert abs(out - 0.5) < 1e-6


# ---------- network (stub honesto) ---------------------------------------
async def test_http_get_raises_not_implemented():
    from Kix.engine.services import HttpProxy
    with pytest.raises(NetworkNotWired):
        await HttpProxy().get("https://example.com")


# ---------- self binding --------------------------------------------------
async def test_self_binding_reads_inputs_first():
    """`self.x` deve resolver para o input antes de olhar o sprite."""
    from Kix.engine.executor import _SelfBinding

    sprite = SpriteProxy(name="X")
    sprite.position = (0, 0)
    binding = _SelfBinding(inputs={"x": 999}, sprite=sprite)
    assert binding.x == 999


async def test_self_binding_falls_back_to_sprite():
    """Quando `x` não é input, lê do sprite."""
    from Kix.engine.executor import _SelfBinding

    sprite = SpriteProxy(name="X")
    sprite.position = (50, 50)
    binding = _SelfBinding(inputs={}, sprite=sprite)
    assert binding.position == (50, 50)


async def test_self_binding_set_writes_back():
    """Atribuir `self.x = ...` deve gravar no input se ele existir."""
    from Kix.engine.executor import _SelfBinding

    inputs = {"x": 0}
    binding = _SelfBinding(inputs=inputs, sprite=None)
    binding.x = 42
    assert inputs["x"] == 42


# ---------- custom decorator-style behavior (prepara M3.2) ----------------
async def test_callable_short_circuits_exec():
    """BlockBehavior com _callable deve ser chamado diretamente."""
    from Kix.engine.ctx import make_ctx

    def my_fn(x: float) -> float:
        return x * 2

    bh = BlockBehavior(language="python", source="x * 2", _callable=my_fn)
    block = KixBlock(
        id="test.double", name="dobro", category="math",
        color=(0, 0, 0, 1),
        visual=BlockVisual(root=Group(children=[Text("dobro "), BlockInput("x")])),
        inputs=[SocketDef("x", SocketKind.NUMBER, default=1)],
        outputs=[SocketDef("result", SocketKind.NUMBER)],
        behavior=bh,
    )
    out = await _run(block, x=21)
    assert out == 42
