"""Editor de código com numeração de linha (spec seção 3.3).

Componente composto:
- Coluna fixa à esquerda (24dp, ``CODE_GUTTER_W``) com numeração em
  ``--text-muted`` — Label redesenhado a cada mudança de cursor/texto.
- ``TextInput`` multilinha à direita com fonte monoespaçada 14sp,
  fundo ``INPUT_BG`` (mais escuro que o bloco azul ao redor para
  contraste), sem quebra de linha (scroll horizontal), auto-grow
  até ``CODE_MAX_LINES`` linhas, mínimo ``CODE_MIN_LINES`` linhas.

API:
- ``CodeEditor(initial="", min_lines=3)`` → widget
- ``editor.text`` → string com ``\\n``
- ``editor.error_text = "Traceback ..."`` → pisca borda ``DANGER``
  e mostra traceback inline (1–2 linhas); ``None`` para limpar.
- ``editor.set_variables(["self", "sprite", ...])`` → preenche o rodapé
  "⚙ Variáveis expostas" (apenas visual — sem ação; clique abre modal
  no caller).

Nota: Kivy ``TextInput`` não tem syntax highlighting nativo — fica como
TODO. A camada de highlight (Pygments-like com Color spans) exigiria um
renderer customizado sobre ``kivy.graphics.Canvas`` que acompanha o
scroll — fora do escopo desta task.

Tokens consumidos de ``Kix.core.theme``:
- ``INPUT_BG``        — fundo do editor
- ``SURFACE_4``       — borda padrão
- ``EMERALD``         — borda em foco (mesma regra de qualquer input)
- ``DANGER``          — borda em estado de erro
- ``CODE_GUTTER_W``   — largura da coluna de numeração (24dp)
- ``CODE_MIN_LINES``  — altura mínima em linhas (3)
- ``CODE_MAX_LINES``  — altura máxima antes do scroll (12)
"""

from __future__ import annotations

from typing import Sequence

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from Kix.core.theme import (
    CODE_FONT_SIZE,
    CODE_GUTTER_W,
    CODE_MAX_LINES,
    CODE_MIN_LINES,
    DANGER,
    EMERALD,
    INPUT_BG,
    SURFACE_4,
    TEXT_HIGH,
    TEXT_LOW,
    TEXT_MED,
)


Builder.load_string("""
<CodeEditor>:
    orientation: 'horizontal'
    spacing: 0
    padding: 0
    canvas.before:
        Color:
            rgba: root._border_color
        Line:
            width: root._border_width
            rectangle: (self.x, self.y, self.width, self.height)

    CodeGutter:
        id: gutter
        size_hint_x: None
        width: root._gutter_w

    CodeInputArea:
        id: editor
        size_hint_x: 1
        background_color: root._editor_bg
        foreground_color: root._fg
        cursor_color: root._fg
        hint_text_color: root._hint
        font_size: root._font_size
        font_name: root._font_name
        multiline: True
        write_tab: False
""")


class CodeGutter(Label):
    """Coluna de numeração de linha (1, 2, 3, ...).

    Texto é atualizado pelo ``CodeEditor`` sempre que o número de
    linhas do editor muda. Cor fixa ``TEXT_LOW`` (spec: --text-muted).
    Alinhamento à direita, padding interno 4dp.
    """

    def __init__(self, **kw):
        super().__init__(
            color=TEXT_LOW,
            font_size="12sp",
            halign="right",
            valign="top",
            padding=(dp(4), dp(6), dp(4), dp(6)),
            **kw,
        )


class CodeInputArea(TextInput):
    """TextInput com tweaks para o code editor.

    - ``do_wrap=False`` — sem quebra de linha (scroll horizontal)
    - Ao mudar texto, propaga evento para o pai redesenhar a gutter.
    """

    def __init__(self, **kw):
        super().__init__(**kw)
        self.do_wrap = False
        self.bind(text=self._on_text_changed)

    def _on_text_changed(self, _inst, _text: str) -> None:
        parent = self.parent
        if parent is None or not hasattr(parent, "_refresh_gutter"):
            return
        parent._refresh_gutter()


class CodeEditor(BoxLayout):
    """Editor de código composto (gutter + textarea) — spec 3.3.

    Parâmetros:
        ``initial``     — texto inicial (default "")
        ``min_lines``   — altura mínima em linhas (default ``CODE_MIN_LINES``)
        ``max_lines``   — altura máxima antes do scroll
                         (default ``CODE_MAX_LINES``)
        ``error_text``  — traceback curto; ``None`` para limpar.
    """

    _border_color = SURFACE_4
    _border_width = 1.0
    _editor_bg = INPUT_BG
    _fg = TEXT_HIGH
    _hint = TEXT_MED
    _font_size = CODE_FONT_SIZE
    _font_name = "RobotoMono-Regular"   # fallback Kivy se não existir
    _gutter_w = CODE_GUTTER_W
    _min_lines = CODE_MIN_LINES
    _max_lines = CODE_MAX_LINES
    _error_text: str | None = None
    _variables: tuple[str, ...] = ()

    def __init__(self, initial: str = "",
                 min_lines: int = CODE_MIN_LINES,
                 max_lines: int = CODE_MAX_LINES,
                 **kw):
        super().__init__(**kw)
        self._min_lines = min_lines
        self._max_lines = max_lines
        self._editor_bg = INPUT_BG
        # line height empírico ~font_size * 1.35 em fontes Kivy default
        self._line_h = dp(14) * 1.35

        self._build(initial)

    def _build(self, initial: str) -> None:
        editor = self.ids.editor
        editor.text = initial
        self._refresh_gutter()
        self._refresh_height()
        editor.bind(focus=self._on_focus,
                    texture_size=self._on_texture_size)

    def _on_focus(self, _inst, focused: bool) -> None:
        if focused:
            self._border_color = EMERALD
            self._border_width = 2.0
        else:
            self._border_color = SURFACE_4 if self._error_text is None else DANGER
            self._border_width = 1.0
        self.canvas.before.clear()

    def _on_texture_size(self, _inst, _tex) -> None:
        self._refresh_height()

    def _refresh_gutter(self) -> None:
        text = self.ids.editor.text
        n_lines = max(1, text.count("\n") + 1)
        # Mostra pelo menos _min_lines linhas na coluna (altura visual
        # da textarea) para o bloco "respirar" mesmo vazio.
        shown = max(n_lines, self._min_lines)
        self.ids.gutter.text = "\n".join(str(i) for i in range(1, shown + 1))

    def _refresh_height(self) -> None:
        text = self.ids.editor.text
        n_lines = max(1, text.count("\n") + 1)
        # Quantas linhas a textarea está exibindo (clamped entre min/max)?
        shown = min(max(n_lines, self._min_lines), self._max_lines)
        # auto-grow: altura = shown * line_height + paddings verticais (~24)
        target = int(shown * self._line_h) + dp(24)
        self.height = target

    # --- API pública ------------------------------------------------------

    @property
    def text(self) -> str:
        return self.ids.editor.text

    @text.setter
    def text(self, value: str) -> None:
        self.ids.editor.text = value
        self._refresh_gutter()
        self._refresh_height()

    @property
    def error_text(self) -> str | None:
        return self._error_text

    @error_text.setter
    def error_text(self, value: str | None) -> None:
        """Define/limpa traceback inline.

        Em estado de erro: borda ``DANGER``. A exibição do traceback
        em si é responsabilidade do caller (popup renderiza um Label
        com o texto retornado aqui).
        """
        self._error_text = value
        if value is None:
            focused = self.ids.editor.focus
            self._border_color = EMERALD if focused else SURFACE_4
            self._border_width = 2.0 if focused else 1.0
        else:
            self._border_color = DANGER
            self._border_width = 2.0
        self.canvas.before.clear()

    def set_variables(self, names: Sequence[str]) -> None:
        """Popula a lista de variáveis expostas (footer "⚙ Variáveis")."""
        self._variables = tuple(names)
