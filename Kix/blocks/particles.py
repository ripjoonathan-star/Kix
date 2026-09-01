"""Blocos de partículas (emissão, controle)."""

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
from Kix.core.theme import CAT_PARTICLES


PART_EMIT = KixBlock(
    id="particles.emit", name="Emitir partículas", category="particles", color=CAT_PARTICLES,
    visual=BlockVisual(root=Group(children=[Text("Emitir "), BlockInput("count"), Text(" partículas")])),
    inputs=[SocketDef("count", SocketKind.NUMBER, default=10)],
    outputs=[],
    behavior=BlockBehavior("python", "particles.emit(int(self.count))"),
    permissions={"particles"},
)
PART_SET_LIFETIME = KixBlock(
    id="particles.set_lifetime", name="Vida da partícula", category="particles", color=CAT_PARTICLES,
    visual=BlockVisual(root=Group(children=[Text("Vida = "), BlockInput("seconds"), Text(" s")])),
    inputs=[SocketDef("seconds", SocketKind.NUMBER, default=1.0)],
    outputs=[],
    behavior=BlockBehavior("python", "particles.lifetime = self.seconds"),
    permissions={"particles"},
)
PART_SET_SPEED = KixBlock(
    id="particles.set_speed", name="Velocidade", category="particles", color=CAT_PARTICLES,
    visual=BlockVisual(root=Group(children=[Text("Velocidade = "), BlockInput("speed")])),
    inputs=[SocketDef("speed", SocketKind.NUMBER, default=100)],
    outputs=[],
    behavior=BlockBehavior("python", "particles.speed = self.speed"),
    permissions={"particles"},
)
PART_SET_SPREAD = KixBlock(
    id="particles.set_spread", name="Espalhamento", category="particles", color=CAT_PARTICLES,
    visual=BlockVisual(root=Group(children=[Text("Spread = "), BlockInput("spread"), Text("°")])),
    inputs=[SocketDef("spread", SocketKind.ANGLE, default=30)],
    outputs=[],
    behavior=BlockBehavior("python", "particles.spread = self.spread"),
    permissions={"particles"},
)
PART_SET_COLOR = KixBlock(
    id="particles.set_color", name="Cor", category="particles", color=CAT_PARTICLES,
    visual=BlockVisual(root=Group(children=[Text("Cor = "), BlockInput("color")])),
    inputs=[SocketDef("color", SocketKind.COLOR, default=(1, 0.9, 0.4, 1))],
    outputs=[],
    behavior=BlockBehavior("python", "particles.color = self.color"),
    permissions={"particles"},
)
PART_SET_GRAVITY = KixBlock(
    id="particles.set_gravity", name="Gravidade das partículas", category="particles", color=CAT_PARTICLES,
    visual=BlockVisual(root=Group(children=[Text("Gravidade = "), BlockInput("g")])),
    inputs=[SocketDef("g", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior("python", "particles.gravity = self.g"),
    permissions={"particles"},
)
PART_STOP = KixBlock(
    id="particles.stop", name="Parar partículas", category="particles", color=CAT_PARTICLES,
    visual=BlockVisual(root=Group(children=[Text("Parar emissão")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior("python", "particles.stop()"),
    permissions={"particles"},
)
PART_COUNT = KixBlock(
    id="particles.count", name="Qtd partículas", category="particles", color=CAT_PARTICLES,
    visual=BlockVisual(root=Group(children=[Text("Partículas ativas")])),
    inputs=[],
    outputs=[SocketDef("count", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return particles.alive_count"),
    permissions={"particles"},
)

PARTICLES = (PART_EMIT, PART_SET_LIFETIME, PART_SET_SPEED, PART_SET_SPREAD,
             PART_SET_COLOR, PART_SET_GRAVITY, PART_STOP, PART_COUNT)

assert len(PARTICLES) == 8, f"esperado 8, obtido {len(PARTICLES)}"