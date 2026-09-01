"""Tela "Meu ator ou objeto" com sub-abas Scripts | Looks | Sounds.

Replica a navegação Pocket Code:
- App bar: ← / "Meu ator ou objeto" / kebab (⋮)
- Tabs horizontais: 📋 Scripts | 👁 Looks | 🔊 Sounds
- Conteúdo da aba ativa
- FAB ▶ (play) + FAB + (verde) canto inferior direito
"""

from __future__ import annotations

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from Kix.core.theme import (
    EMERALD,
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
from Kix.projects.model import KixObject
from Kix.ui.button import IconButton


# --- tab widget -----------------------------------------------------------

_TABS = (
    {"key": "scripts", "label": "Scripts", "glyph": "📋"},
    {"key": "looks", "label": "Looks", "glyph": "👁"},
    {"key": "sounds", "label": "Sounds", "glyph": "🔊"},
)


class _TabButton(BoxLayout):
    """Tab horizontal com ícone + label."""

    def __init__(self, glyph: str, label: str, on_release, **kwargs):
        super().__init__(**kwargs)
        self._on_release = on_release
        self.orientation = "vertical"
        self.padding = [dp(6), dp(6), dp(6), dp(6)]
        self.size_hint_y = None
        self.height = dp(48)

        with self.canvas.before:
            self._bg_color = Color(*SURFACE_2)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[RADIUS_SM]
            )
        self.bind(pos=self._sync, size=self._sync, on_touch_down=self._on_touch)

        icon_lbl = Label(
            text=glyph,
            font_size="16sp",
            color=TEXT_HIGH,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(20),
        )
        icon_lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(icon_lbl)

        text_lbl = Label(
            text=label,
            font_size="11sp",
            color=TEXT_MED,
            halign="center",
            valign="middle",
        )
        text_lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(text_lbl)

    def set_selected(self, value: bool) -> None:
        self._bg_color.rgba = SURFACE_3 if value else SURFACE_2

    def _sync(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _on_touch(self, _w, touch):
        if not self.collide_point(*touch.pos):
            return False
        self._bg_color.rgba = SURFACE_4
        from kivy.clock import Clock
        Clock.schedule_once(lambda *_: setattr(self._bg_color, "rgba", SURFACE_2), 100)
        self._on_release()
        return True


# --- content placeholders -------------------------------------------------

class _EmptyContent(BoxLayout):
    """Conteúdo vazio: 'Toque em + para adicionar ...'"""

    def __init__(self, what: str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(24), dp(48), dp(24), dp(48)]
        self.spacing = dp(8)

        lbl = Label(
            text=what,
            color=TEXT_MED,
            font_size="15sp",
            halign="center",
            valign="middle",
        )
        lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(lbl)

        sub = Label(
            text="Toque em '+' para adicionar.",
            color=TEXT_LOW,
            font_size="13sp",
            halign="center",
            valign="middle",
        )
        sub.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.add_widget(sub)


# --- screen principal -----------------------------------------------------

class ObjectScreen(Screen):
    """Tela do objeto com sub-abas Scripts/Looks/Sounds.

    API:
        load_object(obj: KixObject) — define o objeto exibido.
        go_back() — callback de voltar.
    """

    def __init__(self, on_back=None, on_play=None, **kwargs):
        super().__init__(**kwargs)
        self._on_back = on_back or (lambda: None)
        self._on_play = on_play or (lambda: None)
        self._object: KixObject | None = None
        self._current_tab: str = "scripts"
        self._tab_buttons: dict[str, _TabButton] = {}
        self._contents: dict[str, BoxLayout] = {}

        self._build()

    # --- build -----------------------------------------------------------
    def _build(self) -> None:
        with self.canvas.before:
            Color(*SURFACE_1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        # FloatLayout para conter tudo + FABs
        root = FloatLayout()
        self.add_widget(root)

        # coluna principal
        col = BoxLayout(orientation="vertical")
        root.add_widget(col)

        col.add_widget(self._build_topbar())
        col.add_widget(self._build_tab_bar())
        col.add_widget(self._build_content())

        # FAB play (verde)
        play = IconButton(glyph="▶", primary=True)
        play.size_hint = (None, None)
        play.size = (dp(56), dp(56))
        play.x = self.width - dp(72)
        play.y = dp(96)
        play.bind(on_release=lambda *_: self._on_play())
        root.add_widget(play)
        self._play_fab = play
        self.bind(pos=self._sync_fabs, size=self._sync_fabs)

        # FAB + (verde, abaixo do play)
        plus = IconButton(glyph="+", primary=True)
        plus.size_hint = (None, None)
        plus.size = (dp(56), dp(56))
        plus.x = self.width - dp(72)
        plus.y = dp(32)
        plus.bind(on_release=lambda *_: self._on_add())
        root.add_widget(plus)
        self._plus_fab = plus

    def _sync_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _sync_fabs(self, *_):
        if hasattr(self, "_play_fab") and self._play_fab is not None:
            self._play_fab.x = self.width - dp(72)
            self._play_fab.y = dp(96)
        if hasattr(self, "_plus_fab") and self._plus_fab is not None:
            self._plus_fab.x = self.width - dp(72)
            self._plus_fab.y = dp(32)

    # --- topbar ----------------------------------------------------------
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
        bar.bind(
            pos=lambda *_: setattr(bar_bg, "pos", bar.pos),
            size=lambda *_: setattr(bar_bg, "size", bar.size),
        )

        back = IconButton(glyph="‹", primary=False)
        back.size_hint = (None, None)
        back.size = (dp(40), dp(40))
        back.bind(on_release=lambda *_: self._on_back())
        bar.add_widget(back)

        title = Label(
            text="Meu ator ou objeto",
            color=TEXT_HIGH,
            font_size="16sp",
            bold=True,
            halign="center",
            valign="middle",
        )
        title.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        bar.add_widget(title)

        kebab = IconButton(glyph="⋮", primary=False)
        kebab.size_hint = (None, None)
        kebab.size = (dp(40), dp(40))
        kebab.bind(on_release=lambda *_: self._show_object_menu())
        bar.add_widget(kebab)
        return bar

    # --- tab bar ---------------------------------------------------------
    def _build_tab_bar(self) -> BoxLayout:
        bar = BoxLayout(
            size_hint_y=None,
            height=dp(56),
            padding=[dp(8), dp(4), dp(8), dp(4)],
            spacing=dp(8),
        )
        for spec in _TABS:
            btn = _TabButton(
                glyph=spec["glyph"],
                label=spec["label"],
                on_release=lambda k=spec["key"]: self.set_tab(k),
            )
            bar.add_widget(btn)
            self._tab_buttons[spec["key"]] = btn
        # marca Scripts como selecionado
        self._tab_buttons["scripts"].set_selected(True)
        return bar

    # --- content ---------------------------------------------------------
    def _build_content(self) -> BoxLayout:
        self._content_box = BoxLayout(orientation="vertical")
        return self._content_box

    def _render_content(self) -> None:
        self._content_box.clear_widgets()
        for spec in _TABS:
            if spec["key"] == self._current_tab:
                if spec["key"] == "scripts":
                    txt = "Sem scripts ainda"
                elif spec["key"] == "looks":
                    txt = "Sem looks (aparências)"
                else:
                    txt = "Sem sounds (sons)"
                self._content_box.add_widget(_EmptyContent(what=txt))
                break

    # --- API pública ------------------------------------------------------
    def load_object(self, obj: KixObject) -> None:
        self._object = obj

    def set_tab(self, key: str) -> None:
        if key not in self._tab_buttons:
            return
        self._current_tab = key
        for k, btn in self._tab_buttons.items():
            btn.set_selected(k == key)
        self._render_content()

    def _on_add(self) -> None:
        # Stub: M8 terá dialog de adicionar Script/Look/Sound
        from kivy.clock import Clock
        Clock.schedule_once(lambda *_: None, 0)

    def _show_object_menu(self) -> None:
        """Abre o DropdownMenu de contexto do objeto."""
        from Kix.ui.menu import DropdownMenu

        def _make(key, label, glyph):
            return {
                "key": key,
                "label": label,
                "glyph": glyph,
                "on_select": lambda s, k=key: self._handle_action(k),
            }

        items = [
            _make("backpack", "Mochila", "🎒"),
            _make("copy", "Copiar", "⎘"),
            _make("delete", "Apagar", "🗑"),
            _make("rename", "Mudar nome", "✎"),
            _make("new_group", "Novo grupo", "📁"),
            _make("new_scene", "Nova cena", "🎬"),
            _make("details", "Mostrar detalhes", "ⓘ"),
            _make("project_options", "Opções do projeto", "⚙"),
            _make("project_files", "Arquivos do projeto", "📂"),
            _make("project_libs", "Bibliotecas do projeto", "📚"),
            _make("3d_editor", "3D Editor", "🧊"),
        ]
        menu = DropdownMenu(items=items, anchor_widget=self._current_kebab_anchor())
        if self.parent is not None:
            self.parent.add_widget(menu)

    def _current_kebab_anchor(self):
        """Retorna o último IconButton do topbar como anchor."""
        # pegamos o kebab criado no topbar (último filho)
        topbar = self.children[0].children[0]  # root.col.children[0]
        # pega último IconButton da topbar
        from Kix.ui.button import IconButton
        for child in reversed(list(topbar.children)):
            if isinstance(child, IconButton):
                return child
        return None

    def _handle_action(self, key: str) -> None:
        """Stub: roteia ação do menu. M7.4 implementa handlers reais."""
        if key == "backpack":
            self._open_backpack()
        elif key == "copy":
            self._copy_object()
        elif key == "delete":
            self._delete_object()
        elif key == "rename":
            self._rename_object()
        elif key == "new_group":
            self._new_group()
        elif key == "new_scene":
            self._new_scene()
        # restantes ficam como stubs (toast "em breve")

    # --- handlers reais (M7.4) ------------------------------------------
    def _copy_object(self) -> None:
        # Stub: duplica o objeto dentro do mesmo projeto.
        if self._object is None:
            return
        # Persistência é responsabilidade do EditorScreen.

    def _delete_object(self) -> None:
        if self._object is None:
            return

    def _rename_object(self) -> None:
        # Stub: EditorScreen injeta dialog de rename.
        pass

    def _new_group(self) -> None:
        pass

    def _new_scene(self) -> None:
        pass

    def _open_backpack(self) -> None:
        # M8: abre tela Mochila com blocos arrastáveis.
        pass


__all__ = ["ObjectScreen", "KixObject"]