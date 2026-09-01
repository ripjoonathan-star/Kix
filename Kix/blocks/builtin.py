"""Blocos núcleo (originais do M1) + agregação de todos os blocos.

`MOVE`, `SAY`, `WAIT` e `COMPUTE` permanecem aqui com IDs `core.*` por
compatibilidade com testes e projetos salvos antes de M2. Blocos novos
vivem nos módulos por categoria e são importados via `ALL`.
"""

from Kix.block_engine import (
    BlockInput,
    BlockVisual,
    Group,
    KixBlock,
    Number,
    SocketDef,
    SocketKind,
    Text,
)
from Kix.block_engine.behavior import BlockBehavior
from Kix.core.theme import EMERALD, SURFACE_3

# Re-exporta as categorias para uso em `from Kix.blocks.builtin import TRANSFORMS`
from Kix.blocks.transforms import TRANSFORMS            # noqa: F401
from Kix.blocks.visual import VISUAL                    # noqa: F401
from Kix.blocks.runtime import RUNTIME                  # noqa: F401
from Kix.blocks.control import CONTROL                  # noqa: F401
from Kix.blocks.io import IO                            # noqa: F401
from Kix.blocks.network import NETWORK                  # noqa: F401
from Kix.blocks.world import WORLD                      # noqa: F401
from Kix.blocks.ui import UI as UI_BLOCKS               # noqa: F401
from Kix.blocks.math_blocks import MATH_BLOCKS          # noqa: F401
from Kix.blocks.strings import STRINGS                  # noqa: F401
from Kix.blocks.physics import PHYSICS                  # noqa: F401
from Kix.blocks.particles import PARTICLES              # noqa: F401
from Kix.blocks.audio_advanced import AUDIO_ADV         # noqa: F401
from Kix.blocks.scenes import SCENES                    # noqa: F401
from Kix.blocks.ai import AI                            # noqa: F401
from Kix.blocks.storage import STORAGE_BLOCKS           # noqa: F401
from Kix.blocks.notifications import NOTIFICATIONS      # noqa: F401
from Kix.blocks.arvr import ARVR                        # noqa: F401


# --- Bloco núcleo (M1) ------------------------------------------------------
MOVE = KixBlock(
    id="core.move",
    name="Mover",
    category="motion",
    color=EMERALD,
    visual=BlockVisual(root=Group(
        label=None,
        children=[Text("Mover "), BlockInput("steps"), Text(" passos")],
    )),
    inputs=[SocketDef("steps", SocketKind.NUMBER, default=10)],
    outputs=[],
    behavior=BlockBehavior(
        language="python",
        source="self.translate(self.steps, 0)",
    ),
    permissions={"stage"},
)

SAY = KixBlock(
    id="core.say",
    name="Dizer",
    category="looks",
    color=SURFACE_3,
    visual=BlockVisual(root=Group(
        children=[Text("Dizer "), BlockInput("message"), Text(" por "),
                  BlockInput("duration"), Text(" s")],
    )),
    inputs=[
        SocketDef("message", SocketKind.STRING, default="Olá!"),
        SocketDef("duration", SocketKind.NUMBER, default=2.0),
    ],
    outputs=[],
    behavior=None,
    permissions={"stage"},
)

WAIT = KixBlock(
    id="core.wait",
    name="Esperar",
    category="control",
    color=SURFACE_3,
    visual=BlockVisual(root=Group(
        children=[Text("Esperar "), BlockInput("seconds"), Text(" s")],
    )),
    inputs=[SocketDef("seconds", SocketKind.NUMBER, default=1.0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await self.wait(self.seconds)"),
    permissions=set(),
)

COMPUTE = KixBlock(
    id="core.compute",
    name="Calcular",
    category="math",
    color=EMERALD,
    visual=BlockVisual(root=Group(
        children=[Text("Calcular "), BlockInput("expr")],
    )),
    inputs=[SocketDef("expr", SocketKind.STRING, default="1 + 1")],
    outputs=[SocketDef("result", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return eval(expr)"),
    permissions=set(),
)


# --- Agregadores ------------------------------------------------------------
CORE = (MOVE, SAY, WAIT, COMPUTE)
BUILTINS = CORE                          # nome histórico preservado

from Kix.blocks.formula import FORMULA_BLOCKS                # noqa: E402
from Kix.blocks.sensors import SENSORS                       # noqa: E402
from Kix.blocks.hardware import HARDWARE_BLOCKS              # noqa: E402
from Kix.blocks.gestures import GESTURES_BLOCKS             # noqa: E402
from Kix.blocks.layer import LAYERS                          # noqa: E402
from Kix.blocks.event import EVENTS                          # noqa: E402

ALL = (CORE
       + TRANSFORMS
       + VISUAL
       + RUNTIME
       + CONTROL
       + IO
       + NETWORK
       + WORLD
       + UI_BLOCKS
       + MATH_BLOCKS
       + STRINGS
       + PHYSICS
       + PARTICLES
       + AUDIO_ADV
       + SCENES
       + AI
       + STORAGE_BLOCKS
       + NOTIFICATIONS
       + ARVR
       + FORMULA_BLOCKS
       + SENSORS
       + HARDWARE_BLOCKS
       + GESTURES_BLOCKS
       + LAYERS
       + EVENTS)

__all__ = [
    "MOVE", "SAY", "WAIT", "COMPUTE",
    "CORE", "BUILTINS", "ALL",
    "TRANSFORMS", "VISUAL", "RUNTIME", "CONTROL",
    "IO", "NETWORK", "WORLD", "UI_BLOCKS",
    "MATH_BLOCKS", "STRINGS", "PHYSICS", "PARTICLES",
    "AUDIO_ADV", "SCENES", "AI", "STORAGE_BLOCKS",
    "NOTIFICATIONS", "ARVR",
    "FORMULA_BLOCKS", "SENSORS", "HARDWARE_BLOCKS", "GESTURES_BLOCKS",
    "LAYERS",
]