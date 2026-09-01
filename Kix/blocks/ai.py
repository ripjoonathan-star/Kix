"""Blocos de IA: pathfinding, follow, flee, wander."""

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
from Kix.core.theme import CAT_AI


AI_PATHFIND = KixBlock(
    id="ai.pathfind", name="Pathfinding", category="ai", color=CAT_AI,
    visual=BlockVisual(root=Group(children=[Text("Pathfinding até "), BlockInput("target")])),
    inputs=[SocketDef("target", SocketKind.OBJECT)],
    outputs=[],
    behavior=BlockBehavior("python", "await self.pathfind_to(self.target)"),
    permissions={"ai"},
)
AI_FOLLOW = KixBlock(
    id="ai.follow", name="Seguir", category="ai", color=CAT_AI,
    visual=BlockVisual(root=Group(children=[Text("Seguir "), BlockInput("target"), Text(" velocidade "), BlockInput("speed")])),
    inputs=[SocketDef("target", SocketKind.OBJECT),
            SocketDef("speed", SocketKind.NUMBER, default=100)],
    outputs=[],
    behavior=BlockBehavior("python", "self.follow(self.target, self.speed)"),
    permissions={"ai"},
)
AI_FLEE = KixBlock(
    id="ai.flee", name="Fugir de", category="ai", color=CAT_AI,
    visual=BlockVisual(root=Group(children=[Text("Fugir de "), BlockInput("threat"), Text(" velocidade "), BlockInput("speed")])),
    inputs=[SocketDef("threat", SocketKind.OBJECT),
            SocketDef("speed", SocketKind.NUMBER, default=100)],
    outputs=[],
    behavior=BlockBehavior("python", "self.flee(self.threat, self.speed)"),
    permissions={"ai"},
)
AI_WANDER = KixBlock(
    id="ai.wander", name="Vagar", category="ai", color=CAT_AI,
    visual=BlockVisual(root=Group(children=[Text("Vagar velocidade "), BlockInput("speed"), Text(" raio "), BlockInput("radius")])),
    inputs=[SocketDef("speed", SocketKind.NUMBER, default=50),
            SocketDef("radius", SocketKind.NUMBER, default=200)],
    outputs=[],
    behavior=BlockBehavior("python", "self.wander(self.speed, self.radius)"),
    permissions={"ai"},
)
AI_LOOK_DIR = KixBlock(
    id="ai.look_direction", name="Olhar direção", category="ai", color=CAT_AI,
    visual=BlockVisual(root=Group(children=[Text("Olhar para direção "), BlockInput("direction"), Text("°")])),
    inputs=[SocketDef("direction", SocketKind.ANGLE, default=0)],
    outputs=[],
    behavior=BlockBehavior("python", "self.rotation = self.direction"),
    permissions={"ai"},
)
AI_DISTANCE_CHECK = KixBlock(
    id="ai.distance_check", name="Dentro do alcance?", category="ai", color=CAT_AI,
    visual=BlockVisual(root=Group(children=[Text("Distância até "), BlockInput("target"), Text(" ≤ "), BlockInput("max_dist")])),
    inputs=[SocketDef("target", SocketKind.OBJECT),
            SocketDef("max_dist", SocketKind.NUMBER, default=200)],
    outputs=[SocketDef("in_range", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return self.distance_to(self.target) <= self.max_dist"),
    permissions={"ai"},
)

AI = (AI_PATHFIND, AI_FOLLOW, AI_FLEE, AI_WANDER, AI_LOOK_DIR, AI_DISTANCE_CHECK)

assert len(AI) == 6, f"esperado 6, obtido {len(AI)}"