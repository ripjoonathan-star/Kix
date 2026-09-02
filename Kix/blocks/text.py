"""Blocos da categoria Texto — formatação rich text (M8).

Permite customização fina de textos renderizados: tamanho, cor (full
ou por caractere), contorno (cor/espessura/on/off), sombra, gradiente
vertical/horizontal, negrito e itálico. Diferente de ``ui.update_text``
(apenas conteúdo), estes blocos mexem em propriedades visuais do texto.

Cor da categoria: ``CAT_TEXT`` (``#6B7280`` slate-500 neutro) — distinta
de ``CAT_EXTRAS`` e ``CAT_TILEMAP`` por temperatura (neutro) e saturação
(baixa). Spec M8: "texto totalmente customizável, otimizado".
"""

from __future__ import annotations

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
from Kix.core.theme import CAT_TEXT


TEXT_SET_SIZE = KixBlock(
    id="text.set_size",
    name="Definir tamanho do texto",
    category="text",
    color=CAT_TEXT,
    visual=BlockVisual(root=Group(children=[Text("Texto "), BlockInput("id"), Text(" tamanho "), BlockInput("size"), Text(" sp")])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("size", SocketKind.NUMBER, default=14)],
    outputs=[],
    behavior=BlockBehavior("python", "ui.texts[self.id].font_size = float(self.size)"),
    permissions={"ui"},
)

TEXT_SET_COLOR = KixBlock(
    id="text.set_color",
    name="Definir cor do texto",
    category="text",
    color=CAT_TEXT,
    visual=BlockVisual(root=Group(children=[Text("Texto "), BlockInput("id"), Text(" cor "), BlockInput("color")])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("color", SocketKind.COLOR, default=(1, 1, 1, 1))],
    outputs=[],
    behavior=BlockBehavior("python", "ui.texts[self.id].color = tuple(self.color)"),
    permissions={"ui"},
)

TEXT_SET_COLOR_RANGE = KixBlock(
    id="text.set_color_range",
    name="Cor por trecho de texto",
    category="text",
    color=CAT_TEXT,
    visual=BlockVisual(root=Group(children=[
        Text("Texto "), BlockInput("id"),
        Text(" chars "), BlockInput("start"),
        Text("–"), BlockInput("end"),
        Text(" cor "), BlockInput("color"),
    ])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("start", SocketKind.NUMBER, default=0),
            SocketDef("end", SocketKind.NUMBER, default=1),
            SocketDef("color", SocketKind.COLOR, default=(1, 1, 1, 1))],
    outputs=[],
    behavior=BlockBehavior("python",
        "ui.texts[self.id].set_range_color(int(self.start), int(self.end), tuple(self.color))"),
    permissions={"ui"},
)

TEXT_OUTLINE_SET = KixBlock(
    id="text.outline_set",
    name="Definir contorno do texto",
    category="text",
    color=CAT_TEXT,
    visual=BlockVisual(root=Group(children=[
        Text("Texto "), BlockInput("id"),
        Text(" contorno cor "), BlockInput("color"),
        Text(" espessura "), BlockInput("width"),
    ])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("color", SocketKind.COLOR, default=(0, 0, 0, 1)),
            SocketDef("width", SocketKind.NUMBER, default=1.5)],
    outputs=[],
    behavior=BlockBehavior("python",
        "ui.texts[self.id].outline = (tuple(self.color), float(self.width))"),
    permissions={"ui"},
)

TEXT_OUTLINE_TOGGLE = KixBlock(
    id="text.outline_toggle",
    name="Ligar/desligar contorno",
    category="text",
    color=CAT_TEXT,
    visual=BlockVisual(root=Group(children=[
        Text("Texto "), BlockInput("id"),
        Text(" contorno "), BlockInput("on"),
    ])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("on", SocketKind.BOOLEAN, default=True)],
    outputs=[],
    behavior=BlockBehavior("python",
        "ui.texts[self.id].outline_enabled = bool(self.on)"),
    permissions={"ui"},
)

TEXT_SET_SHADOW = KixBlock(
    id="text.set_shadow",
    name="Definir sombra do texto",
    category="text",
    color=CAT_TEXT,
    visual=BlockVisual(root=Group(children=[
        Text("Texto "), BlockInput("id"),
        Text(" sombra dx="), BlockInput("dx"),
        Text(" dy="), BlockInput("dy"),
        Text(" cor "), BlockInput("color"),
    ])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("dx", SocketKind.NUMBER, default=2),
            SocketDef("dy", SocketKind.NUMBER, default=2),
            SocketDef("color", SocketKind.COLOR, default=(0, 0, 0, 0.8))],
    outputs=[],
    behavior=BlockBehavior("python",
        "ui.texts[self.id].shadow = (float(self.dx), float(self.dy), tuple(self.color))"),
    permissions={"ui"},
)

TEXT_GRADIENT_VERTICAL = KixBlock(
    id="text.gradient_vertical",
    name="Gradiente vertical",
    category="text",
    color=CAT_TEXT,
    visual=BlockVisual(root=Group(children=[
        Text("Texto "), BlockInput("id"),
        Text(" gradiente "), BlockInput("top"),
        Text(" → "), BlockInput("bottom"),
    ])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("top", SocketKind.COLOR, default=(1, 1, 1, 1)),
            SocketDef("bottom", SocketKind.COLOR, default=(0, 0, 0, 1))],
    outputs=[],
    behavior=BlockBehavior("python",
        "ui.texts[self.id].gradient = ('vertical', tuple(self.top), tuple(self.bottom))"),
    permissions={"ui"},
)

TEXT_GRADIENT_HORIZONTAL = KixBlock(
    id="text.gradient_horizontal",
    name="Gradiente horizontal",
    category="text",
    color=CAT_TEXT,
    visual=BlockVisual(root=Group(children=[
        Text("Texto "), BlockInput("id"),
        Text(" gradiente "), BlockInput("left"),
        Text(" → "), BlockInput("right"),
    ])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("left", SocketKind.COLOR, default=(1, 1, 1, 1)),
            SocketDef("right", SocketKind.COLOR, default=(0, 0, 0, 1))],
    outputs=[],
    behavior=BlockBehavior("python",
        "ui.texts[self.id].gradient = ('horizontal', tuple(self.left), tuple(self.right))"),
    permissions={"ui"},
)

TEXT_BOLD = KixBlock(
    id="text.bold",
    name="Negrito",
    category="text",
    color=CAT_TEXT,
    visual=BlockVisual(root=Group(children=[
        Text("Texto "), BlockInput("id"),
        Text(" negrito "), BlockInput("on"),
    ])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("on", SocketKind.BOOLEAN, default=True)],
    outputs=[],
    behavior=BlockBehavior("python",
        "ui.texts[self.id].bold = bool(self.on)"),
    permissions={"ui"},
)

TEXT_ITALIC = KixBlock(
    id="text.italic",
    name="Itálico",
    category="text",
    color=CAT_TEXT,
    visual=BlockVisual(root=Group(children=[
        Text("Texto "), BlockInput("id"),
        Text(" itálico "), BlockInput("on"),
    ])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("on", SocketKind.BOOLEAN, default=True)],
    outputs=[],
    behavior=BlockBehavior("python",
        "ui.texts[self.id].italic = bool(self.on)"),
    permissions={"ui"},
)


TEXT_BLOCKS = (TEXT_SET_SIZE, TEXT_SET_COLOR, TEXT_SET_COLOR_RANGE,
               TEXT_OUTLINE_SET, TEXT_OUTLINE_TOGGLE, TEXT_SET_SHADOW,
               TEXT_GRADIENT_VERTICAL, TEXT_GRADIENT_HORIZONTAL,
               TEXT_BOLD, TEXT_ITALIC)

assert len(TEXT_BLOCKS) == 10, f"esperado 10, obtido {len(TEXT_BLOCKS)}"
