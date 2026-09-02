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


# ============================================================ Levels (M8 — +10)
# Helpers de progressão de níveis. Diferente de "scenes.*" (navegação
# entre cenas), "level.*" trabalha com progressão tipo jogo: índice,
# save, total, marcação de completo. Útil em jogos com múltiplos níveis.
LEVEL_GOTO = KixBlock(
    id="level.goto", name="Ir para nível", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Ir para nível "), BlockInput("n")])),
    inputs=[SocketDef("n", SocketKind.NUMBER, default=1)],
    outputs=[],
    behavior=BlockBehavior("python", "levels.goto(int(self.n))"),
    permissions={"scenes"},
)
LEVEL_NEXT = KixBlock(
    id="level.next", name="Próximo nível", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Próximo nível")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior("python", "levels.next()"),
    permissions={"scenes"},
)
LEVEL_PREVIOUS = KixBlock(
    id="level.previous", name="Nível anterior", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Nível anterior")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior("python", "levels.previous()"),
    permissions={"scenes"},
)
LEVEL_RESTART = KixBlock(
    id="level.restart", name="Reiniciar nível", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Reiniciar nível")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior("python", "levels.restart()"),
    permissions={"scenes"},
)
LEVEL_SAVE = KixBlock(
    id="level.save", name="Salvar progresso", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Salvar progresso")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior("python", "levels.save()"),
    permissions={"scenes"},
)
LEVEL_LOAD = KixBlock(
    id="level.load", name="Carregar último save", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Carregar último save")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior("python", "levels.load()"),
    permissions={"scenes"},
)
LEVEL_CURRENT = KixBlock(
    id="level.current", name="Número do nível atual", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Número do nível atual")])),
    inputs=[],
    outputs=[SocketDef("n", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return levels.current"),
    permissions={"scenes"},
)
LEVEL_TOTAL = KixBlock(
    id="level.total", name="Total de níveis", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Total de níveis")])),
    inputs=[],
    outputs=[SocketDef("n", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return levels.total"),
    permissions={"scenes"},
)
LEVEL_COMPLETE = KixBlock(
    id="level.complete", name="Marcar nível completo", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Marcar nível "), BlockInput("n"), Text(" completo")])),
    inputs=[SocketDef("n", SocketKind.NUMBER, default=1)],
    outputs=[],
    behavior=BlockBehavior("python", "levels.mark_complete(int(self.n))"),
    permissions={"scenes"},
)
LEVEL_RESET_ALL = KixBlock(
    id="level.reset_all", name="Resetar todos os saves", category="scenes", color=CAT_SCENES,
    visual=BlockVisual(root=Group(children=[Text("Resetar todos os saves")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior("python", "levels.reset_all()"),
    permissions={"scenes"},
)


SCENES = (SCENE_SWITCH, SCENE_CURRENT, SCENE_COUNT, SCENE_EXISTS,
          # Levels (M8)
          LEVEL_GOTO, LEVEL_NEXT, LEVEL_PREVIOUS, LEVEL_RESTART,
          LEVEL_SAVE, LEVEL_LOAD, LEVEL_CURRENT, LEVEL_TOTAL,
          LEVEL_COMPLETE, LEVEL_RESET_ALL)

assert len(SCENES) == 14, f"esperado 14 (4 base + 10 Levels), obtido {len(SCENES)}"