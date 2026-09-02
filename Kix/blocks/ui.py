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


# ============================================================ Fast UI (M8 — +10)
# Helpers rápidos para controles do sistema (status bar, vibração, teclado,
# orientação). Diferente dos blocos "ui.*" acima (que criam widgets), estes
# mexem em configurações globais do app — sem necessidade de criar widget.
UI_STATUS_BAR_SHOW = KixBlock(
    id="ui.status_bar_show",
    name="Mostrar barra de status",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Mostrar barra de status")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.system.show_status_bar()"),
    permissions={"ui"},
)

UI_STATUS_BAR_HIDE = KixBlock(
    id="ui.status_bar_hide",
    name="Esconder barra de status",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Esconder barra de status")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.system.hide_status_bar()"),
    permissions={"ui"},
)

UI_BLOCK_INPUT = KixBlock(
    id="ui.block_input",
    name="Bloquear toque do usuário",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Bloquear toque do usuário")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.system.input_blocked = True"),
    permissions={"ui"},
)

UI_RELEASE_INPUT = KixBlock(
    id="ui.release_input",
    name="Liberar toque",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Liberar toque")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.system.input_blocked = False"),
    permissions={"ui"},
)

UI_SHOW_KEYBOARD = KixBlock(
    id="ui.show_keyboard",
    name="Mostrar teclado virtual",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Mostrar teclado virtual")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.system.show_keyboard()"),
    permissions={"ui"},
)

UI_HIDE_KEYBOARD = KixBlock(
    id="ui.hide_keyboard",
    name="Esconder teclado virtual",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Esconder teclado virtual")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.system.hide_keyboard()"),
    permissions={"ui"},
)

UI_VIBRATE_SHORT = KixBlock(
    id="ui.vibrate_short",
    name="Vibrar (curto)",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Vibrar curto")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.system.vibrate(ms=30)"),
    permissions={"ui"},
)

UI_VIBRATE_LONG = KixBlock(
    id="ui.vibrate_long",
    name="Vibrar (longo)",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Vibrar longo")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.system.vibrate(ms=200)"),
    permissions={"ui"},
)

UI_ORIENTATION_PORTRAIT = KixBlock(
    id="ui.orientation_portrait",
    name="Travar em retrato",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Travar orientação retrato")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.system.lock_orientation('portrait')"),
    permissions={"ui"},
)

UI_ORIENTATION_LANDSCAPE = KixBlock(
    id="ui.orientation_landscape",
    name="Travar em paisagem",
    category="ui",
    color=CAT_UI,
    visual=BlockVisual(root=Group(children=[Text("Travar orientação paisagem")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="ui.system.lock_orientation('landscape')"),
    permissions={"ui"},
)


UI = (UI_CREATE_BUTTON, UI_BUTTON_LABEL, UI_BUTTON_WAS_CLICKED,
      UI_CREATE_SLIDER, UI_SLIDER_VALUE,
      UI_PROGRESS_BAR, UI_PROGRESS_VALUE,
      UI_CREATE_TEXT, UI_UPDATE_TEXT, UI_HIDE,
      # Fast UI (M8)
      UI_STATUS_BAR_SHOW, UI_STATUS_BAR_HIDE,
      UI_BLOCK_INPUT, UI_RELEASE_INPUT,
      UI_SHOW_KEYBOARD, UI_HIDE_KEYBOARD,
      UI_VIBRATE_SHORT, UI_VIBRATE_LONG,
      UI_ORIENTATION_PORTRAIT, UI_ORIENTATION_LANDSCAPE)

assert len(UI) == 20, f"esperado 20 (10 base + 10 Fast UI), obtido {len(UI)}"