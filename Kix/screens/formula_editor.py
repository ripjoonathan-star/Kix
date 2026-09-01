"""Editor de fórmula — replica a tela do Pocket Code.

Layout:
- App bar: ← / "Editor de fórmula" / ↶ undo / 📁 files / ↷ redo
- Header: "Definir variável X para Y" (placeholder)
- Display da expressão (texto branco, tokens coloridos)
- Linha 1: chips [Funções] [Propriedades] [📋] [📁]
- Linha 2: chips [Sensores] [Lógica] [Dado]
- Teclado numérico com operadores:
    7 8 9 ⌫
    4 5 6 ÷ ×
    1 2 3 − +
    ( ) 0 .
    [Abc] (lateral) | [Calcular] (teal, direita)

Avalia a expressão chamando o executor (`BlockExecutor`) sobre um bloco
fórmula quando o usuário aperta "Calcular".
"""

from __future__ import annotations

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from Kix.core.theme import (
    EMERALD,
    EMERALD_PRESSED,
    RADIUS,
    RADIUS_SM,
    SURFACE_1,
    SURFACE_2,
    SURFACE_3,
    SURFACE_4,
    TEXT_HIGH,
    TEXT_LOW,
    TEXT_MED,
)


# --- sistema de tokens coloridos ------------------------------------------

# Mapa simples de token → cor (RGBA Pocket Code-like).
_TOKEN_COLORS = {
    "NUMBER": (0.20, 0.78, 0.65, 1),     # teal (verde-água)
    "STRING": (0.45, 0.85, 0.55, 1),     # verde claro
    "BOOLEAN": (0.30, 0.55, 0.95, 1),    # azul
    "VARIABLE": (0.95, 0.65, 0.30, 1),   # laranja
    "FUNC": (0.65, 0.55, 0.95, 1),       # roxo claro
    "OPER": (0.93, 0.93, 0.95, 1),       # texto padrão
}


def tokenize(expr: str) -> list[tuple[str, str]]:
    """Tokenização simples: números, strings, identificadores, operadores.

    Retorna lista de (kind, text). Usado pelo display colorido.
    """
    import re

    if not expr:
        return []
    pattern = re.compile(
        r"""
        (?P<number>\d+\.?\d*) |
        (?P<string>"[^"]*") |
        (?P<ident>[A-Za-z_]\w*) |
        (?P<oper>[+\-*/^%()<>!=,])
        """,
        re.VERBOSE,
    )
    tokens: list[tuple[str, str]] = []
    for m in pattern.finditer(expr):
        for kind in ("number", "string", "ident", "oper"):
            val = m.group(kind)
            if val is None:
                continue
            if kind == "number":
                tokens.append(("NUMBER", val))
            elif kind == "string":
                tokens.append(("STRING", val))
            elif kind == "ident":
                low = val.lower()
                if low in ("true", "false"):
                    tokens.append(("BOOLEAN", val))
                elif val in ("sin", "cos", "tan", "sqrt", "abs", "log", "ln", "round", "floor", "ceil"):
                    tokens.append(("FUNC", val))
                else:
                    tokens.append(("VARIABLE", val))
            else:
                tokens.append(("OPER", val))
    return tokens


# --- widgets --------------------------------------------------------------

class _ColorText(Label):
    """Label com tokens coloridos por palavra.

    Renderização simples: cada token vira um Label concatenado em uma BoxLayout.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._box = BoxLayout(
            orientation="horizontal",
            size_hint_x=1,
            size_hint_y=None,
            height=dp(28),
            padding=[dp(12), 0, dp(12), 0],
        )
        self._box.bind(minimum_width=self._update_width)
        self.add_widget(self._box)

    def set_expression(self, expr: str) -> None:
        self._box.clear_widgets()
        for kind, text in tokenize(expr):
            color = _TOKEN_COLORS.get(kind, TEXT_HIGH)
            lbl = Label(
                text=text + " ",
                color=color,
                font_size="18sp",
                halign="left",
                valign="middle",
                size_hint_x=None,
                width=dp(9) * (len(text) + 1),
            )
            lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
            self._box.add_widget(lbl)

    def _update_width(self, _inst, width):
        self._box.width = max(self.width, width)


class _ChipButton(BoxLayout):
    """Chip usado nas linhas Funções/Propriedades/Sensores/Lógica/Dado."""

    def __init__(self, label: str, on_release=None, **kwargs):
        super().__init__(**kwargs)
        self._on_release = on_release
        self.orientation = "vertical"
        self.padding = [dp(10), dp(6), dp(10), dp(6)]
        self.size_hint_y = None
        self.height = dp(36)

        with self.canvas.before:
            self._bg_color = Color(*SURFACE_3)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(18)]
            )
        self.bind(pos=self._sync, size=self._sync, on_touch_down=self._on_touch)

        lbl = Label(
            text=label,
            color=TEXT_MED,
            font_size="12sp",
            halign="center",
            valign="middle",
        )
        lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(lbl)

    def _sync(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _on_touch(self, _w, touch):
        if not self.collide_point(*touch.pos):
            return False
        self._bg_color.rgba = SURFACE_4
        from kivy.clock import Clock
        Clock.schedule_once(lambda *_: setattr(self._bg_color, "rgba", SURFACE_3), 100)
        if self._on_release:
            self._on_release()
        return True


class _Key(BoxLayout):
    """Tecla individual do teclado numérico."""

    def __init__(self, label: str, kind: str = "default", on_release=None, **kwargs):
        super().__init__(**kwargs)
        self._on_release = on_release
        self._kind = kind
        self.padding = [dp(2), dp(2), dp(2), dp(2)]
        with self.canvas.before:
            if kind == "primary":
                bg = (0.063, 0.725, 0.506, 1)
            elif kind == "alt":
                bg = (0.20, 0.55, 0.55, 1)
            else:
                bg = SURFACE_3
            self._bg_color = Color(*bg)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[RADIUS_SM]
            )
        self.bind(pos=self._sync, size=self._sync, on_touch_down=self._on_touch)

        lbl = Label(
            text=label,
            font_size="20sp",
            color=(1, 1, 1, 1) if kind != "default" else TEXT_HIGH,
            halign="center",
            valign="middle",
        )
        lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(lbl)

    def _sync(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _on_touch(self, _w, touch):
        if not self.collide_point(*touch.pos):
            return False
        # efeito: cor mais clara
        from kivy.clock import Clock
        self._bg_color.rgba = SURFACE_4
        Clock.schedule_once(lambda *_: self._reset_color(), 80)
        if self._on_release:
            self._on_release()
        return True

    def _reset_color(self):
        if self._kind == "primary":
            self._bg_color.rgba = EMERALD_PRESSED
        elif self._kind == "alt":
            self._bg_color.rgba = (0.20, 0.55, 0.55, 1)
        else:
            self._bg_color.rgba = SURFACE_3


# --- tela principal -------------------------------------------------------

class FormulaEditorScreen(Screen):
    """Editor de fórmula no estilo Pocket Code."""

    def __init__(self, on_done=None, **kwargs):
        super().__init__(**kwargs)
        self._on_done = on_done or (lambda value: None)
        self._expr: str = ""
        self._undo_stack: list[str] = []
        self._redo_stack: list[str] = []

        with self.canvas.before:
            Color(*SURFACE_1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        root = BoxLayout(orientation="vertical")
        self.add_widget(root)

        root.add_widget(self._build_topbar())
        root.add_widget(self._build_header())
        root.add_widget(self._build_display())
        root.add_widget(self._build_chip_rows())
        root.add_widget(self._build_keypad())

    def _sync_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size

    # --- topbar ---------------------------------------------------------
    def _build_topbar(self) -> BoxLayout:
        bar = BoxLayout(
            size_hint_y=None,
            height=dp(56),
            padding=[dp(8), dp(8), dp(8), dp(8)],
            spacing=dp(8),
        )
        with bar.canvas.before:
            Color(*SURFACE_2)
            bar_bg = RoundedRectangle(pos=bar.pos, size=bar.size, radius=[0])

        def _bg_sync(*_):
            bar_bg.pos = bar.pos
            bar_bg.size = bar.size

        bar.bind(pos=_bg_sync, size=_bg_sync)

        bar.add_widget(self._topbar_btn("‹", primary=False, on_release=self._cancel))
        bar.add_widget(self._title_label())
        bar.add_widget(self._topbar_btn("↶", primary=False, on_release=self._undo))
        bar.add_widget(self._topbar_btn("📁", primary=False, on_release=self._open_files))
        bar.add_widget(self._topbar_btn("↷", primary=False, on_release=self._redo))
        return bar

    def _topbar_btn(self, glyph: str, primary: bool = True, on_release=None):
        from Kix.ui.button import IconButton
        btn = IconButton(glyph=glyph, primary=primary)
        btn.size_hint = (None, None)
        btn.size = (dp(40), dp(40))
        if on_release:
            btn.bind(on_release=lambda *_: on_release())
        return btn

    def _title_label(self) -> Label:
        lbl = Label(
            text="Editor de fórmula",
            color=TEXT_HIGH,
            font_size="16sp",
            bold=True,
            halign="center",
            valign="middle",
        )
        lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        return lbl

    # --- header (Definir variável X para Y) -----------------------------
    def _build_header(self) -> BoxLayout:
        wrap = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            padding=[dp(16), dp(8), dp(16), dp(8)],
            spacing=dp(8),
        )
        with wrap.canvas.before:
            Color(*SURFACE_2)
            wrap_bg = RoundedRectangle(pos=wrap.pos, size=wrap.size, radius=[0])
        wrap.bind(
            pos=lambda *_: setattr(wrap_bg, "pos", wrap.pos),
            size=lambda *_: setattr(wrap_bg, "size", wrap.size),
        )

        var_label = Label(
            text="Definir variável [X] para",
            color=TEXT_MED,
            font_size="13sp",
            halign="left",
            valign="middle",
            size_hint_x=None,
            width=dp(160),
        )
        var_label.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        wrap.add_widget(var_label)

        self._var_input = Label(
            text="[Y]",
            color=TEXT_HIGH,
            font_size="14sp",
            bold=True,
            halign="left",
            valign="middle",
        )
        self._var_input.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        wrap.add_widget(self._var_input)
        return wrap

    # --- display da expressão ------------------------------------------
    def _build_display(self) -> BoxLayout:
        wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(72),
            padding=[dp(8), dp(8), dp(8), dp(8)],
        )
        with wrap.canvas.before:
            Color(*SURFACE_2)
            wrap_bg = RoundedRectangle(
                pos=wrap.pos, size=wrap.size, radius=[RADIUS_SM]
            )
        wrap.bind(
            pos=lambda *_: setattr(wrap_bg, "pos", wrap.pos),
            size=lambda *_: setattr(wrap_bg, "size", wrap.size),
        )

        self._display = _ColorText(
            color=TEXT_HIGH,
            halign="left",
            valign="middle",
        )
        self._display.set_expression("")
        wrap.add_widget(self._display)
        return wrap

    # --- chips Funções/Propriedades/Sensores/Lógica/Dado --------------
    def _build_chip_rows(self) -> BoxLayout:
        wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(96),
            padding=[dp(8), dp(4), dp(8), dp(4)],
            spacing=dp(6),
        )

        # Linha 1: Funções / Propriedades / 📋 / 📁
        row1 = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(6))
        for label in ("Funções", "Propriedades", "📋", "📁"):
            row1.add_widget(_ChipButton(label=label))
        wrap.add_widget(row1)

        # Linha 2: Sensores / Lógica / Dado
        row2 = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(6))
        for label in ("Sensores", "Lógica", "Dado"):
            row2.add_widget(_ChipButton(label=label))
        wrap.add_widget(row2)

        return wrap

    # --- teclado numérico ----------------------------------------------
    def _build_keypad(self) -> BoxLayout:
        wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(280),
            padding=[dp(8), dp(8), dp(8), dp(8)],
            spacing=dp(6),
        )

        rows = [
            ["7", "8", "9", "⌫"],
            ["4", "5", "6", "÷", "×"],
            ["1", "2", "3", "−", "+"],
            ["(", ")", "0", "."],
        ]
        for row in rows:
            grid = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(54), spacing=dp(4))
            for key in row:
                grid.add_widget(_Key(label=key, on_release=lambda k=key: self._on_key(k)))
            wrap.add_widget(grid)

        # Última linha: [Abc] | [Calcular]
        bottom = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(54), spacing=dp(6))
        bottom.add_widget(_Key(label="Abc", kind="alt", on_release=lambda: self._on_key("Abc")))
        bottom.add_widget(_Key(label="Calcular", kind="primary", on_release=self._calculate))
        wrap.add_widget(bottom)
        return wrap

    # --- handlers -------------------------------------------------------
    def _on_key(self, key: str) -> None:
        self._undo_stack.append(self._expr)
        self._redo_stack.clear()
        if key == "⌫":
            self._expr = self._expr[:-1]
        elif key == "Abc":
            # abre teclado de strings (M8)
            return
        elif key == "÷":
            self._expr += "/"
        elif key == "×":
            self._expr += "*"
        elif key == "−":
            self._expr += "-"
        else:
            self._expr += key
        self._display.set_expression(self._expr)

    def _undo(self) -> None:
        if not self._undo_stack:
            return
        self._redo_stack.append(self._expr)
        self._expr = self._undo_stack.pop()
        self._display.set_expression(self._expr)

    def _redo(self) -> None:
        if not self._redo_stack:
            return
        self._undo_stack.append(self._expr)
        self._expr = self._redo_stack.pop()
        self._display.set_expression(self._expr)

    def _open_files(self) -> None:
        # M8: abre lista de projetos para colar bloco (Mochila)
        return

    def _calculate(self) -> None:
        """Avalia a expressão via BlockExecutor.

        Sem runtime gráfico: usa o executor do engine para avaliar um bloco
        fórmula isolado. Falha de sintaxe → toast vermelho no display.
        """
        import asyncio

        from Kix.block_engine.behavior import BlockBehavior
        from Kix.block_engine.block import KixBlock
        from Kix.block_engine.visual import BlockVisual
        from Kix.engine.ctx import make_ctx
        from Kix.engine.executor import BlockExecutor

        if not self._expr.strip():
            return
        try:
            block = KixBlock(
                id="formula.eval",
                name="avaliar",
                category="math",
                color=(0.30, 0.65, 0.85, 1),
                visual=BlockVisual(root=Text(value=str(self._expr))),
                behavior=BlockBehavior(
                    language="python",
                    source=f"return ({self._expr})",
                ),
            )
            executor = BlockExecutor()
            ctx = make_ctx()
            coro = executor.run_block(block, ctx=ctx, inputs={})
            try:
                asyncio.get_running_loop()
                from kivy.clock import Clock
                def _step(_dt):
                    import asyncio as _a
                    fut = _a.ensure_future(coro)
                    fut.add_done_callback(self._on_calc_done)
                Clock.schedule_once(_step, 0)
                return
            except RuntimeError:
                pass
            result = asyncio.run(coro)
            self._on_calc_value(result)
        except Exception as e:
            self._display.set_expression(f"⚠ {e}")

    def _on_calc_done(self, fut) -> None:
        try:
            self._on_calc_value(fut.result())
        except Exception as e:
            self._display.set_expression(f"⚠ {e}")

    def _on_calc_value(self, value) -> None:
        self._display.set_expression(str(value))
        self._on_done(value)

    def _cancel(self) -> None:
        if self.parent is not None:
            self.parent.remove_widget(self)
        self._on_done(None)

    # --- API pública ----------------------------------------------------
    def set_expression(self, expr: str) -> None:
        self._expr = expr
        self._display.set_expression(expr)


__all__ = ["FormulaEditorScreen", "tokenize"]