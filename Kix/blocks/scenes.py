"""Blocos de gerenciamento de cenas."""

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
from Kix.core.theme import CAT_SCENES


SCENE_SWITCH = KixBlock(
    id="scene.switch", name="Mudar cena", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Mudar para cena "), BlockInput("name")])),
    inputs=[SocketDef("name", SocketKind.SCENE, default="Stage")],
    outputs=[],
    behavior=BlockBehavior("python", "scenes.switch(self.name)"),
    permissions={"scenes"},
)
SCENE_CURRENT = KixBlock(
    id="scene.current", name="Cena atual", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Cena atual")])),
    inputs=[],
    outputs=[SocketDef("name", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return scenes.current.name"),
    permissions={"scenes"},
)
SCENE_COUNT = KixBlock(
    id="scene.count", name="Qtd cenas", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Número de cenas")])),
    inputs=[],
    outputs=[SocketDef("count", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return len(scenes)"),
    permissions={"scenes"},
)
SCENE_EXISTS = KixBlock(
    id="scene.exists", name="Cena existe?", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Cena "), BlockInput("name"), Text(" existe?")])),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[SocketDef("exists", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return self.name in scenes"),
    permissions={"scenes"},
)

SCENES = (SCENE_SWITCH, SCENE_CURRENT, SCENE_COUNT, SCENE_EXISTS)

assert len(SCENES) == 4, f"esperado 4, obtido {len(SCENES)}"