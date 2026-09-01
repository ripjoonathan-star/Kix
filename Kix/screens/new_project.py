"""Diálogo "Criar Jogo" no estilo Pocket Code.

Popup modal com:
- Header com card de ícone quadrado cinza `</>` à esquerda.
- Campo Nome (vermelho quando vazio).
- Campo Versão (default 1.0.0).
- Label "Tipo de tela" + ícones Retrato/Paisagem (selecionável).
- Checkbox "Gerar link de compartilhamento rápido".
- Botões Criar (emerald) / Sair (cinza).

Resultado entregue via callback `on_create(name, settings)`.
"""

from __future__ import annotations

from dataclasses import replace

from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from Kix.core.theme import (
    BG,
    EMERALD,
    EMERALD_PRESSED,
    RADIUS,
    RADIUS_SM,
    SURFACE_2,
    SURFACE_3,
    SURFACE_4,
    TEXT_HIGH,
    TEXT_LOW,
    TEXT_MED,
    PADDING,
    PADDING_SM,
)
from Kix.projects.model import ProjectSettings
from Kix.ui.button import KixButton


class _IconTile(Widget):
    """Quadrado cinza com ícone `</>` desenhado por dentro.

    Usado como o ícone no header do diálogo (Pocket Code).
    """

    def __init__(self, size: float = dp(48), **kwargs):
        super().__init__(**kwargs)
        self.size = (size, size)
        with self.canvas:
            Color(*SURFACE_3)
            self._bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[RADIUS_SM]
            )
            self._fg = Color(1, 1, 1, 1)
            self._lbl = Label(
                text="</>",
                font_size=dp(18),
                color=(1, 1, 1, 1),
            )
        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        # Centraliza o label manualmente (Label é widget, não canvas instruction)
        self._lbl.size = self.size
        self._lbl.pos = (self.x, self.y + dp(2))
        self._lbl.text_size = self.size
        self._lbl.halign = "center"
        self._lbl.valign = "middle"


class _OrientationOption(BoxLayout):
    """Bloco Retrato / Paisagem: ícone + label + seleção visual."""

    selected_color = (0.063, 0.725, 0.506, 0.20)  # emerald translúcido
    unselected_color = SURFACE_3

    def __init__(self, label: str, portrait: bool, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = (PADDING_SM, PADDING_SM)
        self.spacing = dp(6)
        self._label = label
        self._portrait = portrait
        self._selected = False
        self._build()
        self._refresh()

    def _build(self):
        # Ícone: retângulo simulando celular (mais alto ou mais largo).
        from kivy.uix.widget import Widget
        from kivy.graphics import Line

        self._icon = Widget(size_hint=(1, None), height=dp(56))
        with self._icon.canvas:
            self._icon_color = Color(1, 1, 1, 1)
            self._icon_rect = RoundedRectangle(
                pos=self._icon.pos,
                size=self._icon.size,
                radius=[dp(6)],
            )
            self._icon_border = Line(
                rectangle=(*self._icon.pos, *self._icon.size),
                width=dp(1.5),
            )
        self._icon.bind(pos=self._update_icon, size=self._update_icon)

        self._text = Label(
            text=self._label,
            color=TEXT_MED,
            font_size=dp(13),
            size_hint_y=None,
            height=dp(20),
        )
        self.add_widget(self._icon)
        self.add_widget(self._text)

    def _update_icon(self, *_):
        cx, cy = self._icon.center
        if self._portrait:
            w, h = dp(20), dp(40)
        else:
            w, h = dp(40), dp(20)
        self._icon_rect.pos = (cx - w / 2, cy - h / 2)
        self._icon_rect.size = (w, h)
        self._icon_border.rectangle = (cx - w / 2, cy - h / 2, w, h)

    def set_selected(self, value: bool):
        self._selected = value
        self._refresh()

    def _refresh(self):
        with self.canvas:
            if self._selected:
                Color(*self.selected_color)
            else:
                Color(*self.unselected_color)
        # Re-aplica fundo para o BoxLayout em si
        if not hasattr(self, "_bg_rect"):
            with self.canvas.before:
                self._bg_color = Color(*self.unselected_color)
                self._bg_rect = RoundedRectangle(
                    pos=self.pos, size=self.size, radius=[RADIUS_SM]
                )
        else:
            self._bg_color.rgba = (
                self.selected_color if self._selected else self.unselected_color
            )
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size
        self.bind(pos=self._sync_bg, size=self._sync_bg)

    def _sync_bg(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size


class NewProjectDialog(FloatLayout):
    """Popup modal "Criar Jogo".

    Resultado entregue via `on_create(name: str, settings: ProjectSettings)`
    ao clicar em Criar. Cancelar/Sair chama `on_cancel()`.
    """

    DEFAULT_PROJECT_NAME = "Jogo"

    def __init__(
        self,
        on_create,
        on_cancel=None,
        initial_name: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._on_create = on_create
        self._on_cancel = on_cancel or (lambda: None)

        # Backdrop escuro cobrindo o pai.
        with self.canvas.before:
            Color(0, 0, 0, 0.55)
            self._overlay = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_overlay, size=self._sync_overlay)

        # Card central.
        self._card = BoxLayout(
            orientation="vertical",
            padding=[PADDING_LG, PADDING_LG, PADDING_LG, PADDING],
            spacing=dp(14),
            size_hint=(None, None),
            width=dp(360),
            height=dp(560),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        with self._card.canvas.before:
            Color(*SURFACE_2)
            self._card_bg = RoundedRectangle(
                radius=[RADIUS], pos=self._card.pos, size=self._card.size
            )
        self._card.bind(pos=self._sync_card_bg, size=self._sync_card_bg)
        self.add_widget(self._card)

        self._build_header()
        self._build_name_field(initial_name)
        self._build_version_field()
        self._build_orientation()
        self._build_share_checkbox()
        self._build_actions()

    # --- overlay / card --------------------------------------------------------
    def _sync_overlay(self, *_):
        self._overlay.pos = self.pos
        self._overlay.size = self.size

    def _sync_card_bg(self, *_):
        self._card_bg.pos = self._card.pos
        self._card_bg.size = self._card.size

    # --- header -------------------------------------------------------------
    def _build_header(self):
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            spacing=dp(14),
        )
        header.add_widget(_IconTile(size=dp(56)))
        title_box = BoxLayout(orientation="vertical", spacing=dp(2))
        title_box.add_widget(Label(
            text="Criar Jogo",
            color=TEXT_HIGH,
            font_size=dp(18),
            bold=True,
            halign="left",
            valign="bottom",
            size_hint_y=None,
            height=dp(28),
        ))
        title_box.add_widget(Label(
            text="Defina as informações iniciais",
            color=TEXT_LOW,
            font_size=dp(12),
            halign="left",
            valign="top",
            size_hint_y=None,
            height=dp(22),
        ))
        header.add_widget(title_box)
        self._card.add_widget(header)

    # --- campo nome ---------------------------------------------------------
    def _build_name_field(self, initial: str):
        wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(64),
            spacing=dp(4),
        )
        wrap.add_widget(Label(
            text="Nome",
            color=TEXT_MED,
            font_size=dp(12),
            halign="left",
            valign="bottom",
            size_hint_y=None,
            height=dp(20),
        ))

        ti_kwargs = dict(
            text=initial or self.DEFAULT_PROJECT_NAME,
            multiline=False,
            font_size=dp(15),
            foreground_color=TEXT_HIGH,
            background_color=SURFACE_3,
            cursor_color=(1, 1, 1, 1),
            padding=[dp(10), dp(8), dp(10), dp(8)],
            hint_text="Nome do projeto",
        )
        self._name_input = TextInput(**ti_kwargs)
        self._name_input._ti_default_color = TEXT_HIGH  # type: ignore[attr-defined]
        wrap.add_widget(self._name_input)
        # Cor inicial
        self._refresh_name_color()
        self._name_input.bind(text=self._on_name_text)
        self._card.add_widget(wrap)

    def _on_name_text(self, _inst, _value):
        self._refresh_name_color()

    def _refresh_name_color(self):
        empty = not self._name_input.text.strip()
        # Pocket Code: vermelho quando vazio, branco quando preenchido.
        self._name_input.foreground_color = (
            (0.91, 0.30, 0.24, 1) if empty else TEXT_HIGH
        )

    # --- campo versão -------------------------------------------------------
    def _build_version_field(self):
        wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(64),
            spacing=dp(4),
        )
        wrap.add_widget(Label(
            text="Versão",
            color=TEXT_MED,
            font_size=dp(12),
            halign="left",
            valign="bottom",
            size_hint_y=None,
            height=dp(20),
        ))
        self._version_input = TextInput(
            text="1.0.0",
            multiline=False,
            font_size=dp(15),
            foreground_color=TEXT_HIGH,
            background_color=SURFACE_3,
            cursor_color=(1, 1, 1, 1),
            padding=[dp(10), dp(8), dp(10), dp(8)],
        )
        wrap.add_widget(self._version_input)
        self._card.add_widget(wrap)

    # --- tipo de tela -------------------------------------------------------
    def _build_orientation(self):
        wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(120),
            spacing=dp(6),
        )
        wrap.add_widget(Label(
            text="Tipo de tela",
            color=TEXT_MED,
            font_size=dp(12),
            halign="left",
            valign="bottom",
            size_hint_y=None,
            height=dp(20),
        ))

        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(90),
            spacing=dp(10),
        )
        self._opt_portrait = _OrientationOption(label="Retrato", portrait=True)
        self._opt_landscape = _OrientationOption(label="Paisagem", portrait=False)
        self._opt_portrait.set_selected(True)
        for opt in (self._opt_portrait, self._opt_landscape):
            opt.bind(on_touch_down=self._on_opt_tap(opt))
            row.add_widget(opt)
        wrap.add_widget(row)
        self._card.add_widget(wrap)

    def _on_opt_tap(self, opt: "_OrientationOption"):
        def handler(_w, touch):
            if not opt.collide_point(*touch.pos):
                return False
            self._opt_portrait.set_selected(opt is self._opt_portrait)
            self._opt_landscape.set_selected(opt is self._opt_landscape)
            return True
        return handler

    # --- checkbox share -----------------------------------------------------
    def _build_share_checkbox(self):
        wrap = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(32),
            spacing=dp(8),
            padding=[0, dp(2), 0, 0],
        )
        self._share_check = _CheckBox()
        wrap.add_widget(self._share_check)
        wrap.add_widget(Label(
            text="Gerar link de compartilhamento rápido 🔍",
            color=TEXT_MED,
            font_size=dp(13),
            halign="left",
            valign="middle",
        ))
        self._card.add_widget(wrap)

    # --- botões criar / sair -----------------------------------------------
    def _build_actions(self):
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10),
        )
        self._btn_cancel = KixButton(text="Sair")
        self._btn_create = KixButton(text="Criar", primary=True)
        self._btn_cancel.bind(on_release=lambda *_: self._handle_cancel())
        self._btn_create.bind(on_release=lambda *_: self._handle_create())
        row.add_widget(self._btn_cancel)
        row.add_widget(self._btn_create)
        self._card.add_widget(row)

    # --- handlers -----------------------------------------------------------
    def _handle_cancel(self):
        self._on_cancel()

    def _handle_create(self):
        name = self._name_input.text.strip() or self.DEFAULT_PROJECT_NAME
        version = self._version_input.text.strip() or "1.0.0"
        orientation = (
            "portrait" if self._opt_portrait._selected else "landscape"  # noqa: SLF001
        )
        settings = ProjectSettings(
            version=version,
            orientation=orientation,
            share_link=self._share_check.value,
        )
        self._on_create(name, settings)


class _CheckBox(Widget):
    """Checkbox custom (sem dependência extra). Quadrado + check."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (dp(22), dp(22))
        self.value = False
        with self.canvas:
            self._bg_color = Color(*SURFACE_4)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(4)]
            )
            self._check_color = Color(0, 0, 0, 0)
            self._check_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(4)]
            )
        self.bind(pos=self._sync, size=self._sync, on_touch_down=self._on_tap)

    def _sync(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        # Check inset
        inset = dp(4)
        self._check_rect.pos = (self.x + inset, self.y + inset)
        self._check_rect.size = (self.width - 2 * inset, self.height - 2 * inset)

    def _on_tap(self, _w, touch):
        if not self.collide_point(*touch.pos):
            return False
        self.value = not self.value
        self._check_color.rgba = EMERALD if self.value else (0, 0, 0, 0)
        return True


__all__ = ["NewProjectDialog", "ProjectSettings"]