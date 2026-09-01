"""Blocos de UI/HUD: botões, sliders, barra de progresso, textos."""

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
from Kix.core.theme import CAT_UI


# ============================================================ UI (10)
UI_CREATE_BUTTON = KixBlock(
    id="ui.create_button",
    name="Criar botão",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Botão "), BlockInput("id"), Text(" em x:"), BlockInput("x"), Text(" y:"), BlockInput("y"), Text(" texto: "), BlockInput("label")])),
    inputs=[SocketDef("id", SocketKind.STRING, default="btn1"),
            SocketDef("x", SocketKind.NUMBER, default=100),
            SocketDef("y", SocketKind.NUMBER, default=100),
            SocketDef("label", SocketKind.STRING, default="OK")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.button(self.id, self.x, self.y, self.label)"),
    permissions={"ui"},
)

UI_BUTTON_LABEL = KixBlock(
    id="ui.set_button_label",
    name="Definir texto do botão",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Texto do botão "), BlockInput("id"), Text(" = "), BlockInput("label")])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("label", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.buttons[self.id].label = self.label"),
    permissions={"ui"},
)

UI_BUTTON_WAS_CLICKED = KixBlock(
    id="ui.button_clicked",
    name="Botão foi clicado?",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Botão "), BlockInput("id"), Text(" foi clicado?")])),
    inputs=[SocketDef("id", SocketKind.STRING, default="")],
    outputs=[SocketDef("clicked", SocketKind.BOOLEAN)],
    behavior=BlockBehavior(language="python", source="return ui.buttons[self.id].was_clicked"),
    permissions={"ui"},
)

UI_CREATE_SLIDER = KixBlock(
    id="ui.create_slider",
    name="Criar slider",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Slider "), BlockInput("id"), Text(" em x:"), BlockInput("x"), Text(" y:"), BlockInput("y"), Text(" min:"), BlockInput("min"), Text(" max:"), BlockInput("max")])),
    inputs=[SocketDef("id", SocketKind.STRING, default="sl1"),
            SocketDef("x", SocketKind.NUMBER, default=100),
            SocketDef("y", SocketKind.NUMBER, default=200),
            SocketDef("min", SocketKind.NUMBER, default=0),
            SocketDef("max", SocketKind.NUMBER, default=100)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.slider(self.id, self.x, self.y, self.min, self.max)"),
    permissions={"ui"},
)

UI_SLIDER_VALUE = KixBlock(
    id="ui.slider_value",
    name="Valor do slider",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Valor do slider "), BlockInput("id")])),
    inputs=[SocketDef("id", SocketKind.STRING, default="")],
    outputs=[SocketDef("value", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return ui.sliders[self.id].value"),
    permissions={"ui"},
)

UI_PROGRESS_BAR = KixBlock(
    id="ui.create_progress",
    name="Criar barra de progresso",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Barra "), BlockInput("id"), Text(" em x:"), BlockInput("x"), Text(" y:"), BlockInput("y"), Text(" máx:"), BlockInput("max")])),
    inputs=[SocketDef("id", SocketKind.STRING, default="hp"),
            SocketDef("x", SocketKind.NUMBER, default=20),
            SocketDef("y", SocketKind.NUMBER, default=20),
            SocketDef("max", SocketKind.NUMBER, default=100)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.progress(self.id, self.x, self.y, self.max)"),
    permissions={"ui"},
)

UI_PROGRESS_VALUE = KixBlock(
    id="ui.set_progress_value",
    name="Definir valor da barra",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Barra "), BlockInput("id"), Text(" = "), BlockInput("value")])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("value", SocketKind.NUMBER, default=0)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.progress_bars[self.id].value = self.value"),
    permissions={"ui"},
)

UI_CREATE_TEXT = KixBlock(
    id="ui.create_text",
    name="Criar texto",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Texto "), BlockInput("id"), Text(" em x:"), BlockInput("x"), Text(" y:"), BlockInput("y"), Text(" conteúdo: "), BlockInput("content")])),
    inputs=[SocketDef("id", SocketKind.STRING, default="txt1"),
            SocketDef("x", SocketKind.NUMBER, default=20),
            SocketDef("y", SocketKind.NUMBER, default=400),
            SocketDef("content", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.text(self.id, self.x, self.y, self.content)"),
    permissions={"ui"},
)

UI_UPDATE_TEXT = KixBlock(
    id="ui.set_text",
    name="Atualizar texto",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Texto "), BlockInput("id"), Text(" = "), BlockInput("content")])),
    inputs=[SocketDef("id", SocketKind.STRING, default=""),
            SocketDef("content", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.texts[self.id].content = str(self.content)"),
    permissions={"ui"},
)

UI_HIDE = KixBlock(
    id="ui.hide",
    name="Esconder widget",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Esconder "), BlockInput("id")])),
    inputs=[SocketDef("id", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.widgets[self.id].visible = False"),
    permissions={"ui"},
)


UI = (UI_CREATE_BUTTON, UI_BUTTON_LABEL, UI_BUTTON_WAS_CLICKED,
      UI_CREATE_SLIDER, UI_SLIDER_VALUE,
      UI_PROGRESS_BAR, UI_PROGRESS_VALUE,
      UI_CREATE_TEXT, UI_UPDATE_TEXT, UI_HIDE)

assert len(UI) == 10, f"esperado 10, obtido {len(UI)}"