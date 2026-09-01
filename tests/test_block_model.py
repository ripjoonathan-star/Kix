"""Testes do modelo universal de bloco (KixBlock + BlockVisual + Behavior)."""

from __future__ import annotations

import sys
from pathlib import Path

# Permite executar `pytest` da raiz do repo sem instalar o pacote
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Kix.block_engine import (  # noqa: E402
    Angle,
    BlockInput,
    BlockVisual,
    Boolean,
    Dropdown,
    EditableText,
    Group,
    KixBlock,
    Number,
    Position,
    Slider,
    SocketDef,
    SocketKind,
    Text,
    Variable,
)
from Kix.block_engine.behavior import BlockBehavior  # noqa: E402
from Kix.blocks.builtin import BUILTINS, COMPUTE, MOVE, SAY  # noqa: E402
from Kix.core.theme import EMERALD  # noqa: E402


# --- KixBlock --------------------------------------------------------------
def test_move_instantiates_with_expected_shape():
    assert MOVE.id == "core.move"
    assert MOVE.name == "Mover"
    assert MOVE.category == "motion"
    assert MOVE.color == EMERALD
    assert len(MOVE.inputs) == 1
    assert MOVE.inputs[0].kind == SocketKind.NUMBER
    assert MOVE.inputs[0].default == 10
    assert MOVE.outputs == []


def test_compute_has_outputs_and_behavior():
    assert COMPUTE.outputs and COMPUTE.outputs[0].kind == SocketKind.NUMBER
    assert COMPUTE.behavior is not None
    assert COMPUTE.behavior.language == "python"


def test_socket_with_invalid_kind_raises():
    import pytest

    with pytest.raises(ValueError):
        KixBlock(
            id="bad",
            name="x",
            category="y",
            color=(0, 0, 0, 1),
            visual=BlockVisual(root=Text("x")),
            inputs=[SocketDef("n", "NUMBER")],  # type: ignore[arg-type]
        )


def test_anonymous_id_assigned_when_missing():
    block = KixBlock(
        id="",
        name="anon",
        category="misc",
        color=(0, 0, 0, 1),
        visual=BlockVisual(root=Text("a")),
    )
    assert block.id.startswith("anon.")


# --- BlockVisual (árvore) --------------------------------------------------
def test_visual_tree_round_trip_preserves_structure():
    original = BlockVisual(root=Group(
        label="Opções",
        children=[Text("Mover "), BlockInput("steps"), Text(" passos")],
    ))
    data = original.to_dict()
    back = BlockVisual.from_dict(data)
    assert isinstance(back.root, Group)
    assert back.root.label == "Opções"
    assert len(back.root.children) == 3
    assert isinstance(back.root.children[0], Text)
    assert isinstance(back.root.children[1], BlockInput)


def test_all_visual_nodes_serializable():
    """Cada nó visual deve sobreviver a um round-trip sem erro."""
    nodes = [
        Text("x"), Number(5), EditableText(""),
        Boolean(False), Variable("v"), Dropdown(["a", "b"], "a"),
        BlockInput("n"), Slider(0, 10, 5), Angle(90), Position(1, 2),
    ]
    for n in nodes:
        data = _to_dict_node(n)
        assert data["kind"] == type(n).__name__


def _to_dict_node(node):
    from Kix.block_engine.visual import _visual_to_dict
    return _visual_to_dict(node)


# --- Round-trip JSON do KixBlock -------------------------------------------
def test_kixblock_round_trip_dict():
    for b in BUILTINS:
        data = b.to_dict()
        back = KixBlock.from_dict(data)
        assert back.id == b.id
        assert back.name == b.name
        assert back.color == b.color
        assert len(back.inputs) == len(b.inputs)
        assert len(back.outputs) == len(b.outputs)
        assert back.permissions == b.permissions


# --- Behavior --------------------------------------------------------------
def test_block_behavior_round_trip():
    b = BlockBehavior(language="python", source="return 42")
    back = BlockBehavior.from_dict(b.to_dict())
    assert back.language == b.language
    assert back.source == b.source


def test_block_behavior_run_executes_math_sin():
    """M3: BlockBehavior.run(ctx) realmente executa."""
    from Kix.engine.ctx import make_ctx
    from Kix.blocks.math_blocks import MATH_SIN

    ctx = make_ctx()
    out = MATH_SIN.behavior.run(ctx, inputs={"deg": 90})
    assert isinstance(out, float)
    assert abs(out - 1.0) < 1e-6


def test_block_behavior_round_trip_preserves_behavior():
    """M3: KixBlock.from_dict preserva o BlockBehavior (não zera mais)."""
    for b in BUILTINS:
        data = b.to_dict()
        back = KixBlock.from_dict(data)
        if b.behavior is not None:
            assert back.behavior is not None, f"{b.id}: behavior descartado"
            assert back.behavior.source == b.behavior.source
            assert back.behavior.language == b.behavior.language


# --- Smoke: imports que não devem quebrar ---------------------------------
def test_all_builtins_importable_and_unique_ids():
    ids = [b.id for b in BUILTINS]
    assert len(ids) == len(set(ids)), f"IDs duplicados: {ids}"
    assert {"core.move", "core.say", "core.wait", "core.compute"}.issubset(set(ids))


# referências para silenciar unused warnings em alguns linters
_ = (SAY,)