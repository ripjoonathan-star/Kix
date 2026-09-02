"""PalcoTab — stage view + execução real do projeto.

Layout:
- Title bar: nome do projeto + status ('Pronto' / 'Rodando' / 'Erro')
- Stage canvas: desenha o sprite ativo (quadrado + label do nome)
- Output panel: scroll com os eventos que aconteceram durante a execução

`run()` é assíncrono: cria RuntimeContext, executa cada bloco do projeto
em sequência via BlockExecutor, e atualiza o stage periodicamente. Não
faz loop ainda — dispara uma vez. `stop()` cancela.
"""

from __future__ import annotations

import asyncio
import traceback
from typing import Any

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from Kix.block_engine import KixBlock
from Kix.core.theme import (
    BG,
    CARD_BG,
    EMERALD,
    FONT_SIZE_BODY,
    PADDING,
    SURFACE_1,
    TEXT_HIGH,
    TEXT_LOW,
    TEXT_MED,
)
from Kix.engine.ctx import make_ctx
from Kix.engine.executor import BlockExecutor


Builder.load_string(f"""
<StageView>:
    canvas:
        Color:
            rgba: {SURFACE_1[0]:.3f}, {SURFACE_1[1]:.3f}, {SURFACE_1[2]:.3f}, {SURFACE_1[3]}
        Rectangle:
            pos: self.pos
            size: self.size
""")


class StageView(Widget):
    """Canvas do palco — desenha o sprite ativo."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprite = None
        with self.canvas:
            self._sprite_color = Color(*EMERALD)
            self._sprite_rect = Rectangle(pos=self.pos, size=(40, 40))

        self.bind(
            pos=self._reposition_sprite,
            size=self._reposition_sprite,
        )

    def set_sprite(self, sprite_proxy) -> None:
        self.sprite = sprite_proxy
        self._reposition_sprite()

    def _reposition_sprite(self, *_):
        if self.sprite is None:
            return
        x, y = self.sprite.position
        # mapeia coordenadas do runtime (centro, y-up) → pixels Kivy (canto inf-esq, y-down)
        cx, cy = self.center
        # tamanho do sprite (escala)
        sz = max(8, self.sprite.size)
        size_px = (sz, sz)
        # Rotação visual não tratada aqui — desenhamos quadrado simples.
        # Cor: emerald por padrão, branco se invisível
        self._sprite_color.rgba = (
            self.sprite.color if self.sprite.visible else CARD_BG
        )
        # Translada (x,y) do mundo para coordenadas de tela.
        # Assumimos mundo centrado em (cx,cy): x→cx+x, y→cy+y (y-up).
        self._sprite_rect.pos = (cx + x - size_px[0] / 2, cy + y - size_px[1] / 2)
        self._sprite_rect.size = size_px


class PalcoTab(BoxLayout):
    """Aba 'Palco' do editor."""

    def __init__(self, screen, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.screen = screen
        self._task: asyncio.Task | None = None
        self._build()

    def _build(self) -> None:
        self.padding = [dp(12), dp(12), dp(12), dp(12)]
        self.spacing = dp(8)

        # header com status
        header = BoxLayout(size_hint_y=None, height=dp(40))
        self._status = Label(
            text="Pronto",
            font_size="14sp",
            bold=True,
            color=TEXT_MED,
            halign="left",
            valign="middle",
        )
        self._status.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        info_btn = Label(
            text=f"({self.screen.project.name if self.screen.project else 'Sem projeto'})",
            font_size="12sp",
            color=TEXT_LOW,
            halign="right",
            valign="middle",
        )
        info_btn.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        header.add_widget(self._status)
        header.add_widget(info_btn)
        self.add_widget(header)

        # stage
        self.stage = StageView(size_hint_y=0.6)
        self.add_widget(self.stage)

        # log
        self.log_scroll = ScrollView(
            do_scroll_x=False, bar_width=0,
        )
        self.log_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(2),
            padding=[dp(8), dp(8), dp(8), dp(8)],
        )
        self.log_box.bind(minimum_height=self.log_box.setter("height"))
        self.log_scroll.add_widget(self.log_box)
        self.add_widget(self.log_scroll)

        self._set_status("Pronto", TEXT_MED)

    # --- API --------------------------------------------------------------
    def run(self) -> None:
        """Inicia execução do programa atual (não bloqueia)."""
        if self._task is not None and not self._task.done():
            self._log("Já está rodando…")
            return
        project = self.screen.project
        if project is None or not project.blocks:
            self._log("Nada para rodar — adicione blocos na aba Programação.")
            return
        self._clear_log()
        self._set_status("Rodando…", EMERALD)
        self._task = asyncio.ensure_future(self._run(project))

    def reset(self) -> None:
        """Limpa o estado persistido do sprite (volta ao centro)."""
        project = self.screen.project
        if project is None:
            return
        project.state = {}
        self.screen.save()
        if self.stage.sprite is not None:
            self.stage.sprite.position = (0.0, 0.0)
            self.stage.sprite.rotation = 0.0
            self.stage.sprite.size = 100.0
            self.stage._reposition_sprite()
        self._log("Estado do sprite reiniciado.")

    def stop(self) -> None:
        """Cancela a execução em andamento."""
        if self._task is not None and not self._task.done():
            self._task.cancel()
            self._log("Execução cancelada.")
        self._set_status("Parado", TEXT_MED)

    # --- execução ---------------------------------------------------------
    async def _run(self, project) -> None:
        ctx = make_ctx()
        # restaura estado persistido
        self._restore_state(ctx, project)
        self.stage.set_sprite(ctx.stage.active)
        executor = BlockExecutor()

        self._log(f"Iniciando '{project.name}' ({len(project.blocks)} bloco(s))…")
        try:
            for i, bdata in enumerate(project.blocks):
                if asyncio.current_task().cancelled():
                    raise asyncio.CancelledError()
                block = (
                    KixBlock.from_dict(bdata)
                    if isinstance(bdata, dict)
                    else bdata
                )
                # resolve inputs: usa defaults dos sockets do projeto se houverem,
                # caso contrário os defaults do bloco.
                project_inputs = (
                    bdata.get("inputs", []) if isinstance(bdata, dict) else []
                )
                defaults_by_name = {
                    s.get("name"): s.get("default") for s in project_inputs
                }
                inputs = {}
                for s in block.inputs:
                    if s.name in defaults_by_name and defaults_by_name[s.name] is not None:
                        inputs[s.name] = defaults_by_name[s.name]
                    else:
                        inputs[s.name] = s.default

                try:
                    out = await executor.run_block(block, ctx, inputs)
                except Exception as e:
                    self._log(f"#{i + 1} {block.id}: ERRO — {e}")
                    self._set_status("Erro", (1, 0.4, 0.4, 1))
                    return

                if out is not None:
                    self._log(f"#{i + 1} {block.id} → {out!r}")
                else:
                    self._log(f"#{i + 1} {block.id} ✓")
                self.stage._reposition_sprite()
        except asyncio.CancelledError:
            self._log("Cancelado pelo usuário.")
        finally:
            # persiste estado final do sprite
            self._save_state(ctx, project)
            self._set_status("Concluído", TEXT_MED)
            self._task = None

    def _restore_state(self, ctx, project) -> None:
        """Aplica o state persistido ao sprite ativo, se houver."""
        sprite = ctx.stage.active
        state = project.state or {}
        if "position" in state:
            sprite.position = tuple(state["position"])
        if "rotation" in state:
            sprite.rotation = float(state["rotation"])
        if "size" in state:
            sprite.size = float(state["size"])
        if "opacity" in state:
            sprite.opacity = float(state["opacity"])
        if state:
            self._log(
                f"Estado restaurado: pos={tuple(sprite.position)}, "
                f"rot={sprite.rotation:.1f}°, size={sprite.size:.0f}%"
            )

    def _save_state(self, ctx, project) -> None:
        """Persiste o estado do sprite no projeto."""
        sprite = ctx.stage.active
        project.state = {
            "position": [float(sprite.position[0]), float(sprite.position[1])],
            "rotation": float(sprite.rotation),
            "size": float(sprite.size),
            "opacity": float(sprite.opacity),
        }
        self.screen.save()

    # --- log --------------------------------------------------------------
    def _log(self, msg: str) -> None:
        lbl = Label(
            text=msg,
            font_size="12sp",
            color=TEXT_HIGH,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(20),
        )
        lbl.bind(size=lambda i, _: setattr(i, "text_size", i.size))
        self.log_box.add_widget(lbl)
        # scroll to bottom
        Clock.schedule_once(lambda *_: setattr(self.log_scroll, "scroll_y", 0), 0)

    def _clear_log(self) -> None:
        self.log_box.clear_widgets()

    def _set_status(self, text: str, color) -> None:
        self._status.text = text
        self._status.color = color
