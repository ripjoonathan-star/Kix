"""ProgramaçãoTab — paleta filtrada por categoria + canvas editável.

Layout:
┌─────────────────────────────────────────────┐
│ Header: "Programa: X"            "N blocos" │
│ Toolbar categorias (chips horizontais)       │
│ Paleta filtrada (chips horizontais)         │
│ Canvas: stack vertical de blocos do script  │
└─────────────────────────────────────────────┘

Interações:
- Tap em chip de categoria → filtra paleta
- Tap em chip de bloco da paleta → adiciona ao fim do canvas
- Tap em linha do canvas → modal "Editar" com inputs por socket
- Tap em ↑/↓ no canvas → reordena
- Long-press no canvas → drag-to-reorder (em mobile; desktop usa botões)
- ✕ no canvas → remove
"""

from __future__ import annotations

import copy

from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from Kix.block_engine import KixBlock
from Kix.block_engine.visual import Text as VisualText, BlockInput as VisualInput, Group as VisualGroup
from Kix.blocks.builtin import ALL as ALL_BLOCKS
from Kix.core.theme import (
    BLOCK_HEIGHT_2_LINES,
    BLOCK_ICON_SIZE,
    BLOCK_MIN_HEIGHT,
    BLOCK_PADDING_LEFT,
    BLOCK_TEXT_START_X,
    BLOCK_WAVE_AMPLITUDE,
    BUTTON_BG_SECONDARY,
    EMERALD,
    EMERALD_PRESSED,
    FONT_SIZE_BODY,
    FONT_SIZE_META,
    INPUT_BG,
    MODAL_BG,
    MODAL_OVERLAY,
    PADDING,
    PADDING_SM,
    RADIUS_SM,
    SURFACE_3,
    TEXT_HIGH,
    TEXT_LOW,
    TEXT_MED,
    TOUCH_MIN,
    cat_color,
)
from Kix.ui.block_render import (
    draw_bandeirola_bg,
    draw_block_icon,
    draw_python_cobra_icon,
    set_bandeirola_color,
)


CATEGORY_LABELS = {
    "motion": "Movimento", "looks": "Aparência", "sound": "Som",
    "control": "Controle", "event": "Eventos", "data": "Dados",
    "sensing": "Sensores", "device": "Dispositivo", "files": "Arquivos",
    "user": "Usuário", "libs": "Bibliotecas", "camera": "Câmera",
    "network": "Rede", "layers": "Camadas", "shaders": "Shaders",
    "ui": "Interface", "tilemap": "Tilemap", "spritesheet": "Spritesheet",
    "joystick": "Joystick", "math": "Matemática", "strings": "Textos",
    "physics": "Física", "particles": "Partículas",
    "audio_advanced": "Áudio+", "scenes": "Cenas", "ai": "IA",
    "storage": "Banco", "notifications": "Notificações",
    "arvr": "AR/VR", "economy": "Economia", "python": "Python",
}

# Chip de categoria — usa Tom secundário (clareado) para não cansar visualmente.
# Categorias com two-tone canônico (Pocket Code + spec 3.1/3.2) usam
# cat_color(name, 'light'); as demais caem no fallback SURFACE_3.
def _chip_color(category: str) -> tuple:
    twotone = {
        # Pocket Code canônico (spec 2)
        "motion", "looks", "sound", "control", "event", "data",
        "device", "files", "pen",
        # Extras Kix com paleta curada (spec 3.1)
        "physics", "network", "storage", "economy",
        "particles", "ai", "tilemap", "python",
        # Blocos Extras — categoria unificada para hardware/situacional
        # (spec 3.2 / regra 6 da seção 5). Sub-categorias abaixo são
        # mapeadas para este tom único.
        "extras", "camera", "arvr", "joystick", "notifications",
    }
    if category in twotone:
        return cat_color(category, "light")
    if category == "sensing":
        return cat_color("device", "light")
    return SURFACE_3


def _block_label(block: KixBlock) -> str:
    """Extrai um label curto da árvore visual do bloco."""
    root = block.visual.root
    if isinstance(root, VisualGroup):
        parts = []
        for child in root.children:
            if isinstance(child, VisualText):
                parts.append(child.value)
            elif isinstance(child, VisualInput):
                parts.append(f"[{child.socket}]")
        return "".join(parts) or block.name
    return block.name


def _block_text_only(block: KixBlock) -> str:
    """Label sem marcadores de input — só o texto da árvore visual.

    Usado na linha 1 do layout 2-linhas (spec 2.2: "rótulo na primeira
    linha"). Remove os placeholders ``[nome]`` dos BlockInput.
    """
    root = block.visual.root
    if isinstance(root, VisualGroup):
        parts = []
        for child in root.children:
            if isinstance(child, VisualText):
                parts.append(child.value)
            # VisualInput não emite texto na linha 1
        return "".join(parts).strip() or block.name
    return block.name


def _block_params_line(block: KixBlock) -> str:
    """String compacta descrevendo os parâmetros do texto (linha 2).

    Formato: ``"steps=10, dy=0"``. Para blocos sem inputs → string vazia
    (o caller deve checar ``block.inputs`` antes de chamar).
    """
    if not block.inputs:
        return ""
    parts = []
    for s in block.inputs:
        label = s.label or s.name
        val = s.default if s.default is not None else "—"
        parts.append(f"{label}={val}")
    return ", ".join(parts)


def _blocks_by_category() -> dict[str, list[KixBlock]]:
    grouped: dict[str, list[KixBlock]] = {}
    for block in ALL_BLOCKS:
        grouped.setdefault(block.category, []).append(block)
    return grouped


class ProgramacaoTab(BoxLayout):
    """Aba de programação do editor."""

    _ALL_LABEL = "Todos"

    def __init__(self, screen, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.screen = screen
        self._category_filter: str | None = None  # None = "Todos"
        self._toolbar_buttons: dict[str | None, ButtonBehavior] = {}
        self._palette = None
        self._canvas_widget = None
        self._count_label = None
        self._build()

    def _build(self) -> None:
        self.padding = [dp(12), dp(8), dp(12), dp(8)]
        self.spacing = dp(6)

        # ---------- Cabeçalho ----
        header = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        title = Label(
            text=f"Programa: {self.screen.project.name if self.screen.project else '—'}",
            font_size="16sp",
            bold=True,
            color=TEXT_HIGH,
            halign="left",
            valign="middle",
            size_hint_x=0.6,
        )
        title.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self._count_label = Label(
            text="0 blocos",
            font_size="12sp",
            color=TEXT_LOW,
            halign="right",
            valign="middle",
        )
        self._count_label.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        header.add_widget(title)
        header.add_widget(self._count_label)
        self.add_widget(header)

        # ---------- Toolbar de categorias ----
        toolbar_label = Label(
            text="Categoria",
            font_size="11sp",
            color=TEXT_MED,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18),
        )
        toolbar_label.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(toolbar_label)

        toolbar_scroll = ScrollView(
            size_hint_y=None,
            height=dp(36),
            do_scroll_x=True,
            do_scroll_y=False,
            bar_width=0,
        )
        toolbar = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            spacing=dp(6),
            padding=[dp(2), dp(2), dp(2), dp(2)],
        )
        toolbar.bind(minimum_width=toolbar.setter("width"))
        self._toolbar = toolbar
        toolbar_scroll.add_widget(toolbar)
        self.add_widget(toolbar_scroll)

        # ---------- Paleta ----
        palette_label = Label(
            text="Toque para adicionar",
            font_size="11sp",
            color=TEXT_MED,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18),
        )
        palette_label.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(palette_label)

        palette_scroll = ScrollView(
            size_hint_y=None,
            height=dp(72),
            do_scroll_x=True,
            do_scroll_y=False,
            bar_width=0,
        )
        palette_row = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            spacing=dp(8),
            padding=[dp(4), dp(4), dp(4), dp(4)],
        )
        palette_row.bind(minimum_width=palette_row.setter("width"))
        self._palette = palette_row
        palette_scroll.add_widget(palette_row)
        self.add_widget(palette_scroll)

        # ---------- Canvas ----
        canvas_label = Label(
            text="Programa atual",
            font_size="11sp",
            color=TEXT_MED,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18),
        )
        canvas_label.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(canvas_label)

        canvas_scroll = ScrollView(do_scroll_x=False, bar_width=0)
        canvas_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=0,
            padding=[dp(8), dp(8), dp(8), dp(8)],
        )
        canvas_box.bind(minimum_height=canvas_box.setter("height"))
        self._canvas_widget = canvas_box
        canvas_scroll.add_widget(canvas_box)
        self.add_widget(canvas_scroll)

        self._populate_toolbar()
        self._populate_palette()
        self._refresh_canvas()

    # --- toolbar de categorias -------------------------------------------
    def _populate_toolbar(self) -> None:
        self._toolbar.clear_widgets()
        self._toolbar_buttons.clear()

        # "Todos"
        all_btn = self._make_filter_chip(self._ALL_LABEL, None)
        self._toolbar.add_widget(all_btn)
        self._toolbar_buttons[None] = all_btn

        # Categorias presentes em ALL
        grouped = _blocks_by_category()
        for cat in sorted(grouped.keys(), key=lambda c: CATEGORY_LABELS.get(c, c)):
            if not grouped[cat]:
                continue
            label = CATEGORY_LABELS.get(cat, cat)
            btn = self._make_filter_chip(label, cat)
            self._toolbar.add_widget(btn)
            self._toolbar_buttons[cat] = btn

        self._refresh_toolbar_selection()

    def _make_filter_chip(self, label: str, cat: str | None) -> ButtonBehavior:
        from Kix.ui.button import KixButton

        btn = KixButton(text=label)
        btn._primary = False
        btn.font_size = "12sp"
        btn.size_hint = (None, None)
        btn.width = max(dp(60), len(label) * dp(7) + dp(16))
        btn.height = dp(28)
        btn._tab_key = cat
        btn.bind(on_release=lambda *_: self._set_filter(cat))
        return btn

    def _set_filter(self, cat: str | None) -> None:
        self._category_filter = cat
        self._refresh_toolbar_selection()
        self._populate_palette()

    def _refresh_toolbar_selection(self) -> None:
        for k, btn in self._toolbar_buttons.items():
            is_selected = (k == self._category_filter)
            # reseta attrs para forçar re-render via _on_state
            btn._primary = is_selected
            btn._bg_color.rgba = EMERALD if is_selected else BUTTON_BG_SECONDARY

    # --- paleta -------------------------------------------------------------
    def _populate_palette(self) -> None:
        self._palette.clear_widgets()
        grouped = _blocks_by_category()
        if self._category_filter is None:
            blocks = list(ALL_BLOCKS)
        else:
            blocks = grouped.get(self._category_filter, [])
        for block in blocks:
            chip = _BlockChip(block)
            chip.bind(on_release=lambda inst, b=block: self._add_block(b))
            self._palette.add_widget(chip)

        if not blocks:
            empty = Label(
                text="(vazio)",
                font_size="12sp",
                color=TEXT_LOW,
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(48),
            )
            empty.bind(size=lambda i, _: setattr(i, "text_size", i.size))
            self._palette.add_widget(empty)

    # --- canvas -------------------------------------------------------------
    def _refresh_canvas(self) -> None:
        self._canvas_widget.clear_widgets()
        project = self.screen.project
        if project is None or not project.blocks:
            empty = Label(
                text="Toque em blocos acima para começar",
                font_size="12sp",
                color=TEXT_LOW,
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(60),
            )
            empty.bind(size=lambda i, _: setattr(i, "text_size", i.size))
            self._canvas_widget.add_widget(empty)
            self._count_label.text = "0 blocos"
            return

        for i, bdata in enumerate(project.blocks):
            try:
                if isinstance(bdata, dict):
                    block = KixBlock.from_dict(bdata)
                else:
                    block = bdata
                row = _CanvasRow(
                    block, index=i,
                    on_remove=self._remove_block,
                    on_move_up=self._move_block_up,
                    on_move_down=self._move_block_down,
                    on_edit=self._edit_block,
                )
                self._canvas_widget.add_widget(row)
            except Exception as e:
                err = Label(
                    text=f"#{i}: erro ao carregar bloco ({e})",
                    font_size="11sp",
                    color=(1, 0.4, 0.4, 1),
                    size_hint_y=None,
                    height=dp(28),
                )
                err.bind(size=lambda i, _: setattr(i, "text_size", i.size))
                self._canvas_widget.add_widget(err)
        self._count_label.text = f"{len(project.blocks)} bloco(s)"

    # --- mutação do projeto -----------------------------------------------
    def _add_block(self, block: KixBlock) -> None:
        project = self.screen.project
        if project is None:
            return
        # deep copy — mutações em uma execução não vazam para a paleta
        project.blocks.append(copy.deepcopy(block).to_dict())
        self.screen.save()
        self._refresh_canvas()

    def _remove_block(self, index: int) -> None:
        project = self.screen.project
        if project is None or not (0 <= index < len(project.blocks)):
            return
        del project.blocks[index]
        self.screen.save()
        self._refresh_canvas()

    def _move_block_up(self, index: int) -> None:
        if index <= 0:
            return
        project = self.screen.project
        if project is None:
            return
        project.blocks[index - 1], project.blocks[index] = (
            project.blocks[index], project.blocks[index - 1],
        )
        self.screen.save()
        self._refresh_canvas()

    def _move_block_down(self, index: int) -> None:
        project = self.screen.project
        if project is None or index >= len(project.blocks) - 1:
            return
        project.blocks[index + 1], project.blocks[index] = (
            project.blocks[index], project.blocks[index + 1],
        )
        self.screen.save()
        self._refresh_canvas()

    def _edit_block(self, index: int) -> None:
        """Abre modal para editar os inputs (default values) do bloco."""
        project = self.screen.project
        if project is None or not (0 <= index < len(project.blocks)):
            return
        bdata = project.blocks[index]
        if not isinstance(bdata, dict):
            return

        inputs_meta = bdata.get("inputs", [])
        # --- Categoria "python" → editor de código dedicado (spec 3.3) ---
        # Em vez de TextInputs de 1 linha, usa CodeEditor com numeração
        # de linha, fonte monoespaçada e rodapé "⚙ Variáveis / ▶ Testar".
        if bdata.get("category") == "python":
            self._open_python_code_editor(index, bdata)
            return
        if not inputs_meta:
            # reporter sem input — mostra só "fechar"
            popup = Popup(
                title="",
                content=Label(text="Este bloco não tem inputs editáveis."),
                size_hint=(0.8, None),
                height=dp(120),
                background_color=MODAL_BG,
                overlay_color=MODAL_OVERLAY,
                separator_height=0,
            )
            popup.open()
            return

        box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        title = Label(
            text=f"Editar bloco #{index + 1}",
            font_size="14sp",
            color=TEXT_HIGH,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(24),
        )
        title.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        box.add_widget(title)

        inputs_box = BoxLayout(orientation="vertical", spacing=dp(8))
        input_widgets = {}
        for sock in inputs_meta:
            name = sock.get("name", "?")
            kind = sock.get("kind", "NUMBER")
            default = sock.get("default")
            label = Label(
                text=f"{name} ({kind})",
                font_size="11sp",
                color=TEXT_MED,
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=dp(18),
            )
            label.bind(size=lambda i, _: setattr(i, "text_size", i.size))
            ti = TextInput(
                text=str(default) if default is not None else "",
                multiline=False,
                background_color=INPUT_BG,
                foreground_color=TEXT_HIGH,
                hint_text_color=TEXT_LOW,
                cursor_color=EMERALD,
                padding=[dp(10), dp(8), dp(10), dp(8)],
                font_size="14sp",
                size_hint_y=None,
                height=dp(36),
            )
            input_widgets[name] = (ti, kind)
            inputs_box.add_widget(label)
            inputs_box.add_widget(ti)
        box.add_widget(inputs_box)

        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))
        from Kix.ui.button import KixButton
        cancel = KixButton(text="Cancelar")
        save = KixButton(text="Salvar", primary=True)
        btns.add_widget(cancel)
        btns.add_widget(save)
        box.add_widget(btns)

        popup = Popup(
            title="",
            content=box,
            size_hint=(0.85, None),
            height=dp(60 + 36 * len(inputs_meta) + 24),
            background_color=MODAL_BG,
            overlay_color=MODAL_OVERLAY,
            separator_height=0,
            auto_dismiss=True,
        )

        def _save(*_):
            for sock in inputs_meta:
                name = sock.get("name", "?")
                if name not in input_widgets:
                    continue
                ti, kind = input_widgets[name]
                raw = ti.text
                if kind == "NUMBER":
                    try:
                        sock["default"] = float(raw) if raw else 0
                    except ValueError:
                        sock["default"] = 0
                elif kind == "BOOLEAN":
                    sock["default"] = raw.strip().lower() in ("1", "true", "sim", "yes")
                else:  # STRING, VARIABLE, etc.
                    sock["default"] = raw
            project.blocks[index] = bdata
            self.screen.save()
            popup.dismiss()
            self._refresh_canvas()

        cancel.bind(on_release=lambda *_: popup.dismiss())
        save.bind(on_release=_save)
        popup.open()

    def _open_python_code_editor(self, index: int, bdata: dict) -> None:
        """Popup especial para blocos ``python.exec`` / ``python.eval``.

        Spec 3.3:
        - TextInput multilinha com numeração de linha (CodeEditor)
        - Rodapé com 2 links: "⚙ Variáveis expostas" e "▶ Testar bloco isolado"
        - Erro → borda pisca ``--danger`` + traceback inline (sem modal)
        """
        from Kix.ui.button import KixButton
        from Kix.ui.code_editor import CodeEditor

        inputs_meta = bdata.get("inputs", [])
        # Bloco Python sempre tem 1 input: code (exec) ou expr (eval)
        initial = ""
        sock_name = "code"
        if inputs_meta:
            sock_name = inputs_meta[0].get("name", "code")
            initial = str(inputs_meta[0].get("default", "") or "")

        editor = CodeEditor(initial=initial)
        # Lista de variáveis expostas — popula dinamicamente conforme o
        # objeto onde o bloco está anexado. Spec: "self, sprite, scene,
        # dt, touch, etc.". Aqui devolvemos o conjunto canônico.
        editor.set_variables(("self", "sprite", "scene", "dt", "touch"))

        # --- Rodapé (2 links pequenos, EMERALD_300, sem fundo) -----------
        from Kix.core.theme import EMERALD_300
        from Kix.ui.button import KixButton as _Btn  # noqa: F811

        footer = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(28),
            spacing=dp(16),
            padding=[0, dp(8), 0, 0],
        )
        traceback_label = Label(
            text="",
            color=(0.937, 0.267, 0.267, 1),    # DANGER
            font_size="12sp",
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        traceback_label.bind(
            size=lambda i, _: setattr(i, "text_size", i.size)
        )

        def _show_variables(*_):
            """Modal com lista de variáveis expostas."""
            var_popup = Popup(
                title="Variáveis expostas",
                content=BoxLayout(orientation="vertical", padding=dp(16)),
                size_hint=(0.8, None),
                height=dp(60 + 28 * len(editor._variables) + 16),
                background_color=MODAL_BG,
                overlay_color=MODAL_OVERLAY,
                separator_height=0,
            )
            box = var_popup.content
            for name in editor._variables:
                box.add_widget(Label(
                    text=f"• {name}",
                    font_size="14sp",
                    color=TEXT_HIGH,
                    size_hint_y=None,
                    height=dp(28),
                    halign="left",
                ))
            close = KixButton(text="Fechar", primary=True)
            close.bind(on_release=var_popup.dismiss)
            box.add_widget(close)
            var_popup.open()

        def _test_isolated(*_):
            """Stub: executa o código num sandbox mínimo e mostra erro/sucesso.

            Implementação completa (sandbox + namespace restrito + console
            inline) é responsabilidade do runtime — esta versão só valida
            sintaxe via ``compile()`` para feedback imediato no editor.
            """
            try:
                compile(editor.text, "<bloco>", "exec")
            except SyntaxError as e:
                tb = f"Linha {e.lineno}: {e.msg}"
                traceback_label.text = tb
                editor.error_text = tb
                return
            traceback_label.text = "✓ Sintaxe OK"
            editor.error_text = None

        var_btn = KixButton(
            text="⚙ Variáveis expostas",
            font_size="12sp",
            color=EMERALD_300,
            background_color=(0, 0, 0, 0),
            background_normal="",
        )
        var_btn.color = EMERALD_300
        var_btn.bind(on_release=_show_variables)

        test_btn = KixButton(
            text="▶ Testar bloco isolado",
            font_size="12sp",
            background_color=(0, 0, 0, 0),
            background_normal="",
        )
        test_btn.color = EMERALD_300
        test_btn.bind(on_release=_test_isolated)

        footer.add_widget(var_btn)
        footer.add_widget(test_btn)
        footer.add_widget(traceback_label)

        # --- Botões Cancelar / Salvar ----------------------------------
        btns = BoxLayout(
            size_hint_y=None, height=dp(44), spacing=dp(12)
        )
        cancel = KixButton(text="Cancelar")
        save = KixButton(text="Salvar", primary=True)
        btns.add_widget(cancel)
        btns.add_widget(save)

        box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        title = Label(
            text=f"Editar bloco #{index + 1} — {bdata.get('name', 'Python')}",
            font_size="14sp",
            color=TEXT_HIGH,
            size_hint_y=None,
            height=dp(24),
            halign="left",
        )
        title.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        box.add_widget(title)
        box.add_widget(editor)
        box.add_widget(footer)
        box.add_widget(btns)

        popup = Popup(
            title="",
            content=box,
            size_hint=(0.9, None),
            # Altura: título (24) + editor (~CODE_MIN_LINES * 1.35 * 14dp + 24)
            # + footer (28 + 8) + btns (44) + padding (32) + spacing (24)
            height=dp(180 + 14 * 1.35 * 3 + 24),
            background_color=MODAL_BG,
            overlay_color=MODAL_OVERLAY,
            separator_height=0,
            auto_dismiss=True,
        )

        def _save(*_):
            if inputs_meta:
                inputs_meta[0]["default"] = editor.text
            project.blocks[index] = bdata
            self.screen.save()
            popup.dismiss()
            self._refresh_canvas()

        cancel.bind(on_release=lambda *_: popup.dismiss())
        save.bind(on_release=_save)
        popup.open()


class _BlockChip(ButtonBehavior, BoxLayout):
    """Chip horizontal na paleta: cor da categoria + label do bloco."""

    def __init__(self, block: KixBlock, **kwargs):
        super().__init__(**kwargs)
        self.block = block
        self.size_hint = (None, None)
        self.size = (dp(160), dp(52))
        self.padding = [dp(10), dp(6), dp(10), dp(6)]
        self._build()

    def _build(self) -> None:
        color = _chip_color(self.block.category)
        with self.canvas.before:
            self._bg = Color(*color)
            self._rect = RoundedRectangle(
                radius=[dp(RADIUS_SM)], pos=self.pos, size=self.size
            )
        self.bind(
            pos=lambda i, _: setattr(i._rect, "pos", i.pos),
            size=lambda i, _: setattr(i._rect, "size", i.size),
        )
        label = Label(
            text=_block_label(self.block),
            font_size="12sp",
            color=(1, 1, 1, 1),
            halign="center",
            valign="middle",
            bold=True,
        )
        label.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(label)

        self._orig_color = color
        self.bind(state=self._on_state)

    def _on_state(self, *_):
        if self.state == "down":
            self._bg.rgba = EMERALD_PRESSED
        else:
            self._bg.rgba = self._orig_color


class _CanvasRow(ButtonBehavior, BoxLayout):
    """Linha do canvas: bloco 'bandeirola' + botões ↑ ↓ ✎ ✕ (spec 2.2).

    Layout (esq → dir):
      [ícone 32×32]  [label x=88dp, 18sp, esquerda]  [↑][↓][✎][✕]

    O ícone é desenhado no canvas do widget via ``draw_block_icon`` (não é um
    widget filho — fica abaixo do label e ação, evita capturar toques).
    """

    def __init__(
        self,
        block: KixBlock,
        index: int,
        on_remove,
        on_move_up,
        on_move_down,
        on_edit,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.block = block
        self.index = index
        self.on_remove = on_remove
        self.on_move_up = on_move_up
        self.on_move_down = on_move_down
        self.on_edit = on_edit
        self.size_hint_y = None
        # 2-line layout quando o bloco tem inputs (spec 2.2):
        # linha 1 = rótulo, linha 2 = params. Caso contrário 1 linha.
        self._two_lines = bool(block.inputs)
        self.height = dp(
            BLOCK_HEIGHT_2_LINES if self._two_lines else BLOCK_MIN_HEIGHT
        )
        self.padding = [0, 0, dp(8), 0]
        self._build()

    def _build(self) -> None:
        color = _chip_color(self.block.category)
        self._orig_color = color

        # BoxLayout interno: padding-left = BLOCK_TEXT_START_X (88dp) cria o
        # respiro à esquerda; à direita ficam os botões de ação.
        from Kix.ui.button import IconButton
        inner = BoxLayout(
            orientation="horizontal",
            padding=[dp(BLOCK_TEXT_START_X), dp(8), 0, dp(8)],
            spacing=dp(4),
        )

        # Lado esquerdo: rótulo (1 ou 2 linhas conforme spec 2.2).
        text_box = BoxLayout(
            orientation="vertical",
            spacing=dp(2),
            padding=[0, dp(4), 0, dp(4)],
        )

        # Linha 1 — rótulo do bloco (clicável para editar).
        lbl_btn = _LabelButton(
            text=_block_text_only(self.block),
            font_size="18sp",
            color=TEXT_HIGH,
            bold=False,
            halign="left",
            valign="middle",
        )
        lbl_btn.size_hint_x = 1
        lbl_btn.bind(on_release=lambda *_: self.on_edit(self.index))
        text_box.add_widget(lbl_btn)

        # Linha 2 — params com underline (spec 2.2: "parâmetros na
        # segunda linha @72px do topo, recuo adicional +4px").
        if self._two_lines:
            params_text = _block_params_line(self.block)
            params_btn = _LabelButton(
                text=params_text,
                font_size="14sp",
                color=TEXT_HIGH,
                bold=False,
                halign="left",
                valign="middle",
            )
            # +4px recuo adicional (spec 2.2)
            params_btn.size_hint_x = 1
            text_box.add_widget(params_btn)

        text_box.size_hint_x = 1
        inner.add_widget(text_box)

        # botões de ação (à direita do label)
        for glyph, cb in (
            ("▲", self.on_move_up),
            ("▼", self.on_move_down),
            ("✎", self.on_edit),
            ("✕", self.on_remove),
        ):
            btn = IconButton(glyph=glyph, primary=False)
            btn.size_hint = (None, None)
            btn.size = (dp(32), dp(32))
            btn.bind(on_release=lambda *_, c=cb: c(self.index))
            inner.add_widget(btn)

        self.add_widget(inner)

        # canvas.before: fill da bandeirola + ícone (acima do fill, abaixo
        # dos children). Recriado sempre que size muda.
        self.bind(
            size=lambda *_: self._redraw_canvas(),
            state=self._on_state,
        )
        # Desenho inicial — pode rodar antes do size estar setado; o
        # binding de size refaz quando o layout atribuir dimensões reais.
        self._redraw_canvas()

    def _redraw_canvas(self) -> None:
        """Recria fill da bandeirola + ícone no canvas.before."""
        self.canvas.before.clear()
        self._bg, self._mesh = draw_bandeirola_bg(
            self, self._orig_color, dp(BLOCK_WAVE_AMPLITUDE)
        )
        s = dp(BLOCK_ICON_SIZE)
        x = dp(BLOCK_PADDING_LEFT)
        y = (self.height - s) / 2
        # Spec 3.3: blocos da categoria "python" usam o ícone da cobra
        # (dois arcos entrelaçados) em vez do ícone genérico de página.
        if self.block.category == "python":
            draw_python_cobra_icon(self, x, y, s, canvas=self.canvas.before)
        else:
            draw_block_icon(self, x, y, s, canvas=self.canvas.before)

    def _on_state(self, *_):
        """Estado :down → cor pressionada (emerald)."""
        if hasattr(self, "_bg"):
            set_bandeirola_color(
                self._bg, EMERALD_PRESSED if self.state == "down" else self._orig_color
            )


class _LabelButton(ButtonBehavior, Label):
    """Label clicável — botão invisível só para área de toque."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = "left"
        self.valign = "middle"
        self.bind(size=lambda i, _: setattr(i, "text_size", i.size))
