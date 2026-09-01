"""Blocos AR/VR: iniciar AR, hit test, detectar plano."""

from Kix.block_engine import (
    BlockInput,
    BlockVisual,
    Group,
    KixBlock,
    SocketDef,
    SocketKind,
    Text,
)
from Kix.block_engine.behavior import BlockBehavior
from Kix.core.theme import CAT_ARVR


AR_START = KixBlock(
    id="ar.start", name="Iniciar AR", category="arvr", color=CAT_ARVR,
    visual=BlockVisual(root=Group(children=[Text("Iniciar AR")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior("python", "ar.start()"),
    permissions={"ar", "device"},
)
AR_HIT_TEST = KixBlock(
    id="ar.hit_test", name="Hit test AR", category="arvr", color=CAT_ARVR,
    visual=BlockVisual(root=Group(children=[Text("Hit test no centro da tela")])),
    inputs=[],
    outputs=[SocketDef("hit", SocketKind.BOOLEAN),
             SocketDef("x", SocketKind.NUMBER),
             SocketDef("y", SocketKind.NUMBER),
             SocketDef("z", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return ar.hit_test_center()"),
    permissions={"ar", "device"},
)
AR_PLANE_DETECTED = KixBlock(
    id="ar.plane_detected", name="Plano detectado?", category="arvr", color=CAT_ARVR,
    visual=BlockVisual(root=Group(children=[Text("Plano horizontal detectado?")])),
    inputs=[],
    outputs=[SocketDef("detected", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return ar.has_horizontal_plane"),
    permissions={"ar", "device"},
)

ARVR = (AR_START, AR_HIT_TEST, AR_PLANE_DETECTED)

assert len(ARVR) == 3, f"esperado 3, obtido {len(ARVR)}"