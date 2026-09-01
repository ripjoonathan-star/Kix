"""Blocos de runtime: data (variáveis, listas) + sensing."""

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
from Kix.core.theme import CAT_DATA


# ============================================================ Data (14)
SET_VAR = KixBlock(
    id="data.set",
    name="Definir variável",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Definir "), BlockInput("var"), Text(" = "), BlockInput("value")])),
    inputs=[SocketDef("var", SocketKind.VARIABLE),
            SocketDef("value", SocketKind.STRING, default=0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.var.set(self.value)"),
    permissions={"data"},
)

CHANGE_VAR = KixBlock(
    id="data.change",
    name="Mudar variável",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Mudar "), BlockInput("var"), Text(" por "), BlockInput("delta")])),
    inputs=[SocketDef("var", SocketKind.VARIABLE),
            SocketDef("delta", SocketKind.NUMBER, default=1)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.var.set(self.var.get() + self.delta)"),
    permissions={"data"},
)

SHOW_VAR = KixBlock(
    id="data.show",
    name="Mostrar variável",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Mostrar "), BlockInput("var")])),
    inputs=[SocketDef("var", SocketKind.VARIABLE)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.var.show()"),
    permissions={"data"},
)

HIDE_VAR = KixBlock(
    id="data.hide",
    name="Esconder variável",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Esconder "), BlockInput("var")])),
    inputs=[SocketDef("var", SocketKind.VARIABLE)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.var.hide()"),
    permissions={"data"},
)

LIST_ADD = KixBlock(
    id="data.list_add",
    name="Adicionar à lista",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Adicionar "), BlockInput("value"), Text(" à "), BlockInput("list")])),
    inputs=[SocketDef("value", SocketKind.STRING, default=""),
            SocketDef("list", SocketKind.VARIABLE)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.list.append(self.value)"),
    permissions={"data"},
)

LIST_DELETE_INDEX = KixBlock(
    id="data.list_delete",
    name="Deletar da lista",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Deletar item "), BlockInput("index"), Text(" de "), BlockInput("list")])),
    inputs=[SocketDef("index", SocketKind.NUMBER, default=1),
            SocketDef("list", SocketKind.VARIABLE)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.list.pop(self.index - 1)"),
    permissions={"data"},
)

LIST_DELETE_ALL = KixBlock(
    id="data.list_delete_all",
    name="Limpar lista",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Limpar "), BlockInput("list")])),
    inputs=[SocketDef("list", SocketKind.VARIABLE)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.list.clear()"),
    permissions={"data"},
)

LIST_INSERT = KixBlock(
    id="data.list_insert",
    name="Inserir em",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Inserir "), BlockInput("value"), Text(" em "), BlockInput("index"), Text(" na lista "), BlockInput("list")])),
    inputs=[SocketDef("value", SocketKind.STRING, default=""),
            SocketDef("index", SocketKind.NUMBER, default=1),
            SocketDef("list", SocketKind.VARIABLE)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.list.insert(self.index - 1, self.value)"),
    permissions={"data"},
)

LIST_REPLACE = KixBlock(
    id="data.list_replace",
    name="Substituir item",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Substituir item "), BlockInput("index"), Text(" de "), BlockInput("list"), Text(" por "), BlockInput("value")])),
    inputs=[SocketDef("index", SocketKind.NUMBER, default=1),
            SocketDef("list", SocketKind.VARIABLE),
            SocketDef("value", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.list[self.index - 1] = self.value"),
    permissions={"data"},
)

LIST_ITEM = KixBlock(
    id="data.list_item",
    name="Item de lista",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Item "), BlockInput("index"), Text(" de "), BlockInput("list")])),
    inputs=[SocketDef("index", SocketKind.NUMBER, default=1),
            SocketDef("list", SocketKind.VARIABLE)],
    outputs=[SocketDef("item", SocketKind.STRING)],
    behavior=BlockBehavior(language="python", source="return self.list[self.index - 1]"),
    permissions={"data"},
)

LIST_INDEX_OF = KixBlock(
    id="data.list_index_of",
    name="Índice de",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Índice de "), BlockInput("value"), Text(" em "), BlockInput("list")])),
    inputs=[SocketDef("value", SocketKind.STRING, default=""),
            SocketDef("list", SocketKind.VARIABLE)],
    outputs=[SocketDef("index", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return self.list.index(self.value) + 1"),
    permissions={"data"},
)

LIST_LENGTH = KixBlock(
    id="data.list_length",
    name="Comprimento da lista",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Comprimento de "), BlockInput("list")])),
    inputs=[SocketDef("list", SocketKind.VARIABLE)],
    outputs=[SocketDef("length", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return len(self.list)"),
    permissions={"data"},
)

LIST_CONTAINS = KixBlock(
    id="data.list_contains",
    name="Lista contém",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Lista "), BlockInput("list"), Text(" contém "), BlockInput("value")])),
    inputs=[SocketDef("list", SocketKind.VARIABLE),
            SocketDef("value", SocketKind.STRING, default="")],
    outputs=[SocketDef("contains", SocketKind.BOOLEAN)],
    behavior=BlockBehavior(language="python", source="return self.value in self.list"),
    permissions={"data"},
)

STRING_JOIN = KixBlock(
    id="data.string_join",
    name="Juntar texto",
    category="data",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Juntar "), BlockInput("a"), Text(" com "), BlockInput("b")])),
    inputs=[SocketDef("a", SocketKind.STRING, default=""),
            SocketDef("b", SocketKind.STRING, default="")],
    outputs=[SocketDef("result", SocketKind.STRING)],
    behavior=BlockBehavior(language="python", source="return str(self.a) + str(self.b)"),
    permissions={"data"},
)


# ============================================================ Sensing (10)
SENSING_TOUCHING_MOUSE = KixBlock(
    id="sensing.touching_mouse",
    name="Tocando mouse",
    category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Tocando no mouse?")])),
    inputs=[],
    outputs=[SocketDef("touching", SocketKind.BOOLEAN)],
    behavior=BlockBehavior(language="python", source="return self.collide_point(input.mouse)"),
    permissions={"sensing"},
)

SENSING_TOUCHING_OBJECT = KixBlock(
    id="sensing.touching_object",
    name="Tocando objeto",
    category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Tocando em "), BlockInput("target")])),
    inputs=[SocketDef("target", SocketKind.OBJECT)],
    outputs=[SocketDef("touching", SocketKind.BOOLEAN)],
    behavior=BlockBehavior(language="python", source="return self.collide(self.target)"),
    permissions={"sensing"},
)

SENSING_TOUCHING_COLOR = KixBlock(
    id="sensing.touching_color",
    name="Tocando cor",
    category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Tocando cor "), BlockInput("color")])),
    inputs=[SocketDef("color", SocketKind.COLOR, default=(1, 1, 1, 1))],
    outputs=[SocketDef("touching", SocketKind.BOOLEAN)],
    behavior=BlockBehavior(language="python", source="return self.touching_color(self.color)"),
    permissions={"sensing"},
)

SENSING_DISTANCE = KixBlock(
    id="sensing.distance",
    name="Distância até",
    category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Distância até "), BlockInput("target")])),
    inputs=[SocketDef("target", SocketKind.OBJECT)],
    outputs=[SocketDef("distance", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return self.distance_to(self.target)"),
    permissions={"sensing"},
)

SENSING_ASK = KixBlock(
    id="sensing.ask",
    name="Perguntar",
    category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Perguntar "), BlockInput("question"), Text(" e esperar")])),
    inputs=[SocketDef("question", SocketKind.STRING, default="?")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await self.ask(self.question)"),
    permissions={"sensing"},
)

SENSING_ANSWER = KixBlock(
    id="sensing.answer",
    name="Resposta",
    category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Resposta")])),
    inputs=[],
    outputs=[SocketDef("answer", SocketKind.STRING)],
    behavior=BlockBehavior(language="python", source="return self.last_answer"),
    permissions={"sensing"},
)

SENSING_MOUSE_X = KixBlock(
    id="sensing.mouse_x",
    name="Mouse X",
    category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Posição X do mouse")])),
    inputs=[],
    outputs=[SocketDef("x", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return input.mouse[0]"),
    permissions={"sensing"},
)

SENSING_MOUSE_Y = KixBlock(
    id="sensing.mouse_y",
    name="Mouse Y",
    category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Posição Y do mouse")])),
    inputs=[],
    outputs=[SocketDef("y", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return input.mouse[1]"),
    permissions={"sensing"},
)

SENSING_TIMER = KixBlock(
    id="sensing.timer",
    name="Timer",
    category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Timer")])),
    inputs=[],
    outputs=[SocketDef("seconds", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return self.timer"),
    permissions={"sensing"},
)

SENSING_RESET_TIMER = KixBlock(
    id="sensing.reset_timer",
    name="Resetar timer",
    category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("Resetar timer")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.timer = 0"),
    permissions={"sensing"},
)


# --- M3.3: sensors faltando (5) -------------------------------------------
SENSING_SCREEN_WIDTH = KixBlock(
    id="sensing.screen_width", name="largura da tela", category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("largura da tela")])),
    inputs=[], outputs=[SocketDef("width", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return screen.width"),
    permissions={"sensing"},
)
SENSING_SCREEN_HEIGHT = KixBlock(
    id="sensing.screen_height", name="altura da tela", category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("altura da tela")])),
    inputs=[], outputs=[SocketDef("height", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return screen.height"),
    permissions={"sensing"},
)
SENSING_FPS = KixBlock(
    id="sensing.fps", name="FPS", category="sensing", color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("FPS")])),
    inputs=[], outputs=[SocketDef("fps", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return engine.fps"),
    permissions={"sensing"},
)
SENSING_COLOR_AT = KixBlock(
    id="sensing.color_at_x_y", name="cor em x y", category="sensing",
    color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[Text("cor em x:"), BlockInput("x"), Text(" y:"), BlockInput("y")])),
    inputs=[SocketDef("x", SocketKind.NUMBER, default=0),
            SocketDef("y", SocketKind.NUMBER, default=0)],
    outputs=[SocketDef("color", SocketKind.COLOR)],
    behavior=BlockBehavior("python", "return screen.color_at(self.x, self.y)"),
    permissions={"sensing"},
)
SENSING_COLOR_EQUAL_TOLERANCE = KixBlock(
    id="sensing.color_equal_tolerance", name="cores iguais com tolerância",
    category="sensing", color=CAT_DATA,
    visual=BlockVisual(root=Group(children=[
        Text("cor "), BlockInput("a"), Text(" = "), BlockInput("b"),
        Text(" com tolerância "), BlockInput("tolerance"),
    ])),
    inputs=[SocketDef("a", SocketKind.COLOR, default="#000000"),
            SocketDef("b", SocketKind.COLOR, default="#000000"),
            SocketDef("tolerance", SocketKind.NUMBER, default=0.0)],
    outputs=[SocketDef("result", SocketKind.BOOLEAN)],
    behavior=BlockBehavior("python",
        "return screen.color_equal_with_tolerance(self.a, self.b, self.tolerance)"),
    permissions={"sensing"},
)


RUNTIME = (SET_VAR, CHANGE_VAR, SHOW_VAR, HIDE_VAR,
           LIST_ADD, LIST_DELETE_INDEX, LIST_DELETE_ALL, LIST_INSERT,
           LIST_REPLACE, LIST_ITEM, LIST_INDEX_OF, LIST_LENGTH,
           LIST_CONTAINS, STRING_JOIN,
           SENSING_TOUCHING_MOUSE, SENSING_TOUCHING_OBJECT,
           SENSING_TOUCHING_COLOR, SENSING_DISTANCE, SENSING_ASK,
           SENSING_ANSWER, SENSING_MOUSE_X, SENSING_MOUSE_Y,
           SENSING_TIMER, SENSING_RESET_TIMER,
           SENSING_SCREEN_WIDTH, SENSING_SCREEN_HEIGHT, SENSING_FPS,
           SENSING_COLOR_AT, SENSING_COLOR_EQUAL_TOLERANCE)

assert len(RUNTIME) == 29, f"esperado 29, obtido {len(RUNTIME)}"