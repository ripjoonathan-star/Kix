"""BlockChip — widget que renderiza um KixBlock.

Suporta duas formas:
- **regular**: retângulo arredondado (padrão).
- **hat**: topo convexo arredondado (estilo Pocket Code para eventos).

O desenho é via canvas (Color + Line/Polygon), sem SVG — feito com
primitivas Kivy. O texto e os inputs vêm do `BlockVisual.root` (Group
de Text/BlockInput/Number/etc.) e são renderizados dentro do chip.

Implementação compacta: o chip é uma BoxLayout horizontal; o canvas.before
desenha a forma; os filhos (Text/Input) são labels/widgets adicionados.
"""

from __future__ import annotations

from dataclasses import fields
from typing import Any

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from Kix.block_engine.block import KixBlock
from Kix.block_engine.visual import (
    BlockInput,
    Color as VisColor,
    EditableText,
    Group,
    Number,
    Text as VisText,
    Variable,
)
from Kix.core.theme import PADDING_SM, RADIUS_SM, SURFACE_4, TEXT_HIGH, TEXT_LOW


def _is_text_node(node: Any) -> bool:
    return isinstance(node, VisText)


def _is_input_node(node: Any) -> bool:
    return isinstance(node, BlockInput)


def _is_number_node(node: Any) -> bool:
    return isinstance(node, Number)


def _is_variable_node(node: Any) -> bool:
    return isinstance(node, Variable)


def _is_editable_node(node: Any) -> bool:
    return isinstance(node, EditableText)


def _iter_children(node: Any):
    """Itera filhos de um Group, ou yields o próprio node se for folha."""
    if isinstance(node, Group):
        for c in node.children:
            yield c
    else:
        yield node


class _ChipBackground(Widget):
    """Desenha o fundo do chip (regular ou hat)."""

    def __init__(self, color: tuple, is_hat: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._color = color
        self._is_hat = is_hat
        with self.canvas.before:
            self._c = Color(*color)
            if is_hat:
                # Hat: combinação de semicírculo no topo + retângulo embaixo.
                # Implementação simples: retângulo arredondado com radius generoso.
                self._rect = RoundedRectangle(
                    radius=[dp(RADIUS_SM)], pos=self.pos, size=self.size
                )
                # Linha extra no topo (sugere convexidade)
                self._top = Line(
                    points=[], width=dp(2),
                    cap="round", joint="round",
                )
                self._c_top = Color(color[0]*1.15, color[1]*1.15, color[2]*1.15, 1)
            else:
                self._rect = RoundedRectangle(
                    radius=[dp(RADIUS_SM)], pos=self.pos, size=self.size
                )
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size
        if self._is_hat:
            # arco convexo no topo: semicírculo que sobe ~6dp
            cx = self.x + self.width / 2
            cy = self.top
            r = self.width / 2
            # 16 segmentos para parecer arco
            pts = []
            import math
            steps = 16
            for i in range(steps + 1):
                t = math.pi * i / steps
                px = cx - r * math.cos(t)
                py = cy + r * 0.18 * math.sin(t)
                pts.extend([px, py])
            self._top.points = pts


class BlockChip(BoxLayout):
    """Render visual de um KixBlock.

    Renderiza a árvore `BlockVisual.root` (Text + BlockInput) numa faixa
    horizontal colorida. Se `block.is_hat`, o topo recebe um arco convexo.
    """

    def __init__(self, block: KixBlock, **kwargs):
        super().__init__(**kwargs)
        self._block = block
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(40) if not block.is_hat else dp(44)
        self.padding = [dp(12), dp(8) if not block.is_hat else dp(14),
                        dp(12), dp(8)]
        self.spacing = dp(4)

        # background como primeiro widget (renderiza antes dos filhos)
        bg = _ChipBackground(block.color, is_hat=block.is_hat)
        self.add_widget(bg, index=len(self.children))

        # renderiza conteúdo do visual
        self._render_root(block.visual.root)

    def _render_root(self, root) -> None:
        """Renderiza Group raiz ou nó solto."""
        for node in _iter_children(root):
            self._render_node(node)

    def _render_node(self, node) -> None:
        if _is_text_node(node):
            lbl = Label(
                text=node.value,
                color=TEXT_HIGH,
                font_size="14sp",
                halign="left",
                valign="middle",
            )
            lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
            self.add_widget(lbl)
        elif _is_input_node(node):
            # socket marcador — mostra nome + valor default como input
            socket = node.socket
            default = self._default_for(socket)
            ti = TextInput(
                text=str(default) if default is not None else "",
                font_size="14sp",
                size_hint=(None, None),
                size=(dp(80), dp(28)),
                multiline=False,
                background_color=SURFACE_4,
                foreground_color=TEXT_HIGH,
                padding=[dp(6), dp(4)],
            )
            self.add_widget(ti)
        elif _is_number_node(node):
            ti = TextInput(
                text=str(node.value),
                font_size="14sp",
                size_hint=(None, None),
                size=(dp(60), dp(28)),
                multiline=False,
                input_filter="float",
                background_color=SURFACE_4,
                foreground_color=TEXT_HIGH,
            )
            self.add_widget(ti)
        elif _is_editable_node(node):
            ti = TextInput(
                text=node.value or node.placeholder,
                font_size="14sp",
                size_hint=(None, None),
                size=(dp(80), dp(28)),
                multiline=False,
                background_color=SURFACE_4,
                foreground_color=TEXT_LOW if not node.value else TEXT_HIGH,
            )
            self.add_widget(ti)
        elif _is_variable_node(node):
            var_lbl = Label(
                text=node.name or "var",
                color=(1, 0.85, 0.4, 1),     # laranja
                font_size="14sp",
                halign="left",
                valign="middle",
                bold=True,
            )
            var_lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
            self.add_widget(var_lbl)
        elif isinstance(node, Group):
            for c in node.children:
                self._render_node(c)
        # outros tipos (Color, Slider, Icon, etc) — silenciosamente ignorados

    def _default_for(self, socket: str) -> Any:
        for s in self._block.inputs:
            if s.name == socket:
                return s.default
        return None


__all__ = ["BlockChip"]
