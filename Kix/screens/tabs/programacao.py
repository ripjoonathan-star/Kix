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
    EMERALD,
    EMERALD_PRESSED,
    FONT_SIZE_BODY,
    FONT_SIZE_META,
    PADDING,
    PADDING_SM,
    RADIUS_SM,
    SURFACE_2,
    SURFACE_3,
    SURFACE_4,
    TEXT_HIGH,
    TEXT_LOW,
    TEXT_MED,
    TOUCH_MIN,
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
    "storage": "Armazenamento", "notifications": "Notificações",
    "arvr": "AR/VR",
}

# Cores de "chip" — um pouco mais escuras que a cor da categoria para não cansar.
def _chip_color(category: str) -> tuple:
    from Kix.core.theme import (
        CAT_MOTION, CAT_LOOKS, CAT_SOUND, CAT_CONTROL, CAT_EVENT,
        CAT_DATA, CAT_DEVICE, CAT_FILES, CAT_USER, CAT_LIBS,
        CAT_CAMERA, CAT_NETWORK, CAT_LAYERS, CAT_SHADERS, CAT_UI,
        CAT_TILEMAP, CAT_SPRITESHEET, CAT_JOYSTICK, CAT_MATH, CAT_STRINGS,
        CAT_PHYSICS, CAT_PARTICLES, CAT_AUDIO_ADV, CAT_SCENES, CAT_AI,
        CAT_STORAGE, CAT_NOTIFICATIONS, CAT_ARVR, SURFACE_3,
    )
    return {
        "motion": CAT_MOTION, "looks": CAT_LOOKS, "sound": CAT_SOUND,
        "control": CAT_CONTROL, "event": CAT_EVENT, "data": CAT_DATA,
        "sensing": CAT_DEVICE, "device": CAT_DEVICE, "files": CAT_FILES,
        "user": CAT_USER, "libs": CAT_LIBS, "camera": CAT_CAMERA,
        "network": CAT_NETWORK, "layers": CAT_LAYERS, "shaders": CAT_SHADERS,
        "ui": CAT_UI, "tilemap": CAT_TILEMAP, "spritesheet": CAT_SPRITESHEET,
        "joystick": CAT_JOYSTICK, "math": CAT_MATH, "strings": CAT_STRINGS,
        "physics": CAT_PHYSICS, "particles": CAT_PARTICLES,
        "audio_advanced": CAT_AUDIO_ADV, "scenes": CAT_SCENES, "ai": CAT_AI,
        "storage": CAT_STORAGE, "notifications": CAT_NOTIFICATIONS,
        "arvr": CAT_ARVR,
    }.get(category, SURFACE_3)


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
            spacing=dp(6),
            padding=[dp(4), dp(4), dp(4), dp(4)],
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
            btn._bg_color.rgba = EMERALD if is_selected else SURFACE_3

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
        if not inputs_meta:
            # reporter sem input — mostra só "fechar"
            popup = Popup(
                title="",
                content=Label(text="Este bloco não tem inputs editáveis."),
                size_hint=(0.8, None),
                height=dp(120),
                background_color=SURFACE_2,
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
                background_color=SURFACE_3,
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
            background_color=SURFACE_2,
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
    """Linha do canvas: bloco colorido + botões ↑ ↓ ✎ ✕."""

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
        self.height = dp(48)
        self.padding = [dp(8), dp(4), dp(4), dp(4)]
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

        # índice
        idx = Label(
            text=f"#{self.index + 1}",
            font_size="10sp",
            color=(1, 1, 1, 0.7),
            halign="left",
            valign="middle",
            size_hint_x=None,
            width=dp(28),
        )
        idx.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(idx)

        # label do bloco (clicável para editar)
        lbl_btn = _LabelButton(
            text=_block_label(self.block),
            font_size="13sp",
            color=(1, 1, 1, 1),
            bold=True,
        )
        lbl_btn.bind(on_release=lambda *_: self.on_edit(self.index))
        self.add_widget(lbl_btn)

        # botões de ação
        from Kix.ui.button import IconButton
        up = IconButton(glyph="▲", primary=False)
        up.size_hint = (None, None)
        up.size = (dp(32), dp(32))
        up.bind(on_release=lambda *_: self.on_move_up(self.index))

        down = IconButton(glyph="▼", primary=False)
        down.size_hint = (None, None)
        down.size = (dp(32), dp(32))
        down.bind(on_release=lambda *_: self.on_move_down(self.index))

        edit = IconButton(glyph="✎", primary=False)
        edit.size_hint = (None, None)
        edit.size = (dp(32), dp(32))
        edit.bind(on_release=lambda *_: self.on_edit(self.index))

        rm = IconButton(glyph="✕", primary=False)
        rm.size_hint = (None, None)
        rm.size = (dp(32), dp(32))
        rm.bind(on_release=lambda *_: self.on_remove(self.index))

        self.add_widget(up)
        self.add_widget(down)
        self.add_widget(edit)
        self.add_widget(rm)

        # Suprime o on_release herdado de ButtonBehavior (que dispararia
        # _CanvasRow.on_release — não usado).
        self.bind(on_release=lambda *_: None)


class _LabelButton(ButtonBehavior, Label):
    """Label clicável — botão invisível só para área de toque."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = "left"
        self.valign = "middle"
        self.bind(size=lambda i, _: setattr(i, "text_size", i.size))
