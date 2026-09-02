"""Gestos multitouch + pen + custom variables + broadcast extras.

Catroid inclui:
- Gestos: tap, double tap, swipe, long press, pinch, shake, tilt
- Pen: down, move, up, color, size, clear, stamp
- Custom variables: declare, set, change, show/hide
- Broadcast: when I receive (handler) — implementado como sensor
"""

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
from Kix.core.theme import CAT_DEVICE, CAT_PEN, CAT_DATA, CAT_EVENT, CAT_PHYSICS


# ============================================================ Touch / Gestos
TAP_X = KixBlock(
    id="touch.last_x", name="toque X", category="sensing", color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("X do último toque")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return touch.last_x"),
    permissions={"sensing"},
)
TAP_Y = KixBlock(
    id="touch.last_y", name="toque Y", category="sensing", color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("Y do último toque")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return touch.last_y"),
    permissions={"sensing"},
)
IS_TOUCHED = KixBlock(
    id="touch.is_touched", name="está sendo tocado?", category="sensing", color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("tela sendo tocada?")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python", "return touch.is_touched"),
    permissions={"sensing"},
)
SWIPE = KixBlock(
    id="touch.last_swipe", name="último swipe", category="sensing", color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("direção do último swipe")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return touch.swipe"),
    permissions={"sensing"},
)
TAP_COUNT = KixBlock(
    id="touch.tap_count", name="qtd. toques", category="sensing", color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("contagem de toques")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return touch.tap_count"),
    permissions={"sensing"},
)
SHAKE = KixBlock(
    id="touch.shake", name="shake detectado?", category="sensing", color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("tremeu o dispositivo?")])),
    inputs=[], outputs=[SocketDef("value", SocketKind.BOOLEAN)],
    behavior=BlockBehavior(
        "python",
        "import math; "
        "ax, ay, az = device.accel; "
        "mag = math.sqrt(ax*ax + ay*ay + az*az); "
        "return mag > 2.5",
    ),
    permissions={"sensing"},
)

# ============================================================ Pen
# pen.down / pen.up / pen.clear / pen.color / pen.size / pen.stamp
# já existem em Kix.blocks.visual — não duplicar aqui.
PEN_MOVE = KixBlock(
    id="pen.move_xy", name="mover caneta", category="pen", color=CAT_PEN,
    visual=BlockVisual(root=Group(children=[
        Text("Mover caneta para "), BlockInput("x"), Text(", "), BlockInput("y"),
    ])),
    inputs=[SocketDef("x", SocketKind.NUMBER, default=0),
            SocketDef("y", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior("python", "pen.move(self.x, self.y)"),
    permissions={"pen"},
)

# ============================================================ Custom Variables
# data.list_length / data.list_replace / data.list_contains / data.list_index_of
# já existem em Kix.blocks.runtime — não duplicar aqui.
# Apenas adicionamos: declare, delete, get, declare_list, list_get.
VAR_DECLARE = KixBlock(
    id="data.declare_variable", name="declarar variável", category="data", color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[
        Text("Declarar variável "), BlockInput("name"),
        Text(" = "), BlockInput("value"),
    ])),
    inputs=[SocketDef("name", SocketKind.STRING, default="minha_var"),
            SocketDef("value", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior(
        "python",
        "ctx.variables[self.name] = self.value",
    ),
    permissions={"data"},
)
VAR_DELETE = KixBlock(
    id="data.delete_variable", name="apagar variável", category="data", color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[
        Text("Apagar variável "), BlockInput("name"),
    ])),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior("python", "ctx.variables.pop(self.name, None)"),
    permissions={"data"},
)
VAR_GET = KixBlock(
    id="data.get_variable", name="ler variável", category="data", color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[
        Text("Ler "), BlockInput("name"), Text(" (padrão "), BlockInput("default"), Text(")"),
    ])),
    inputs=[SocketDef("name", SocketKind.STRING, default="score"),
            SocketDef("default", SocketKind.NUMBER, default=0)],
    outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(
        "python",
        "v = ctx.variables.get(self.name); return float(v) if isinstance(v,(int,float)) else float(self.default)",
    ),
    permissions={"data"},
)
LIST_DECLARE = KixBlock(
    id="data.declare_list", name="declarar lista", category="data", color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[
        Text("Declarar lista "), BlockInput("name"),
        Text(" com "), BlockInput("initial"), Text(" itens"),
    ])),
    inputs=[SocketDef("name", SocketKind.STRING, default="itens"),
            SocketDef("initial", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior(
        "python",
        "ctx.variables[self.name] = [] if int(self.initial) <= 0 else list(range(int(self.initial)))",
    ),
    permissions={"data"},
)
LIST_GET = KixBlock(
    id="data.list_get", name="item da lista", category="data", color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[
        Text("Item "), BlockInput("index"), Text(" de "), BlockInput("name"),
    ])),
    inputs=[SocketDef("name", SocketKind.STRING, default=""),
            SocketDef("index", SocketKind.NUMBER, default=1)],
    outputs=[SocketDef("value", SocketKind.STRING)],
    behavior=BlockBehavior(
        "python",
        "lst = ctx.variables.get(self.name, []); "
        "i = int(self.index) - 1; "
        "return lst[i] if 0 <= i < len(lst) else ''",
    ),
    permissions={"data"},
)

# ============================================================ Physics simples
GRAVITY = KixBlock(
    id="physics.gravity", name="gravidade", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[Text("Gravidade "), BlockInput("g")])),
    inputs=[SocketDef("g", SocketKind.NUMBER, default=9.8)],
    outputs=[],
    behavior=BlockBehavior("python", "physics.set_gravity(float(self.g))"),
    permissions={"physics"},
)
WALL = KixBlock(
    id="physics.add_wall", name="adicionar parede", category="physics", color=CAT_PHYSICS,
    visual=BlockVisual(root=Group(children=[
        Text("Parede em x="), BlockInput("x"), Text(", y="), BlockInput("y"),
        Text(" de "), BlockInput("w"), Text("×"), BlockInput("h"),
    ])),
    inputs=[
        SocketDef("x", SocketKind.NUMBER, default=0),
        SocketDef("y", SocketKind.NUMBER, default=0),
        SocketDef("w", SocketKind.NUMBER, default=100),
        SocketDef("h", SocketKind.NUMBER, default=10),
    ],
    outputs=[],
    behavior=BlockBehavior(
        "python",
        "physics.add_wall(self.x, self.y, self.w, self.h)",
    ),
    permissions={"physics"},
)

# ============================================================ Broadcast (when handlers)
# control.clone_start já existe em Kix.blocks.control — apenas adicionamos
# control.when_receive aqui.
WHEN_RECEIVE = KixBlock(
    id="control.when_receive", name="quando receber", category="event", color=CAT_EVENT,
    visual=BlockVisual(root=Group(children=[
        Text("Quando receber "), BlockInput("message"),
        Text(" "), BlockInput("body"),
    ])),
    inputs=[SocketDef("message", SocketKind.STRING, default="game_over"),
            SocketDef("body", SocketKind.BLOCK, default=[])],
    outputs=[],
    behavior=BlockBehavior(
        "python",
        "ctx.services.bus.when(self.message, lambda: None)",
    ),
    permissions={"control"},
)

TOUCH_BLOCKS = (TAP_X, TAP_Y, IS_TOUCHED, SWIPE, TAP_COUNT, SHAKE)
PEN_BLOCKS = (PEN_MOVE,)
DATA_BLOCKS = (VAR_DECLARE, VAR_DELETE, VAR_GET, LIST_DECLARE, LIST_GET)
PHYSICS_BLOCKS = (GRAVITY, WALL)
EVENT_BLOCKS = (WHEN_RECEIVE,)

GESTURES_BLOCKS = TOUCH_BLOCKS + PEN_BLOCKS + DATA_BLOCKS + PHYSICS_BLOCKS + EVENT_BLOCKS
