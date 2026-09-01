"""Contexto de runtime: Stage, SpriteProxy, RuntimeContext, make_ctx.

`RuntimeContext` é o `ctx` passado para `BlockBehavior.run(ctx)`. Ele
agrega:

- `stage` — o palco atual (lista de sprites, sprite ativo, cena atual).
- `services` — proxies para câmera, áudio, tilemap, rede, etc.
- `clock`, `timer`, `answer` — estado compartilhado.
- `variables` — variáveis/lists do projeto (dict por nome).

`SpriteProxy` é o lado de fora do sprite ativo: o `_SelfBinding` do
executor delega `self.<attr>` para cá. Métodos como `translate`,
`wait`, `jump` mutam estado e usam `asyncio.sleep` quando preciso.
"""

from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass, field
from typing import Any

from Kix.engine.services import Services


# --- Sprite proxy ----------------------------------------------------------
@dataclass
class SpriteProxy:
    """Estado mutável do sprite ativo (objeto do projeto).

    O executor conecta `self.<attr>` a este proxy quando há um sprite
    ativo. Atributos cobertos batem com o que os blocos `motion.*` e
    `looks.*` escrevem/leem.
    """

    name: str = "Sprite"
    position: tuple[float, float] = (0.0, 0.0)
    rotation: float = 0.0           # graus
    direction: float = 90.0         # convenção Scratch: 90 = cima
    size: float = 100.0             # percentual
    scale: float = 1.0
    fw: float = 64.0
    fh: float = 64.0
    visible: bool = True
    opacity: float = 1.0
    brightness: float = 1.0
    tint: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    rotation_style: str = "all around"
    layer: int = 0
    z: int = 0
    velocity: tuple[float, float] = (0.0, 0.0)
    mass: float = 1.0
    friction: float = 0.1
    bounce: float = 0.0
    sound: Any = None
    frame_index: int = 0
    current_animation: str = ""
    count: int = 1                  # nº de aparências / frames
    # estado derivado
    on_ground: bool = True

    # ----- comandos ----------------------------------------------------
    def translate(self, dx: float, dy: float) -> None:
        x, y = self.position
        self.position = (x + float(dx), y + float(dy))

    def move_to(self, target) -> None:
        if hasattr(target, "position"):
            self.position = tuple(target.position)
        elif isinstance(target, (list, tuple)) and len(target) >= 2:
            self.position = (float(target[0]), float(target[1]))

    async def slide(self, x: float, y: float, duration: float) -> None:
        # Tween linear simples em N passos; MVP.
        steps = max(1, int(duration * 60))
        sx, sy = self.position
        for i in range(1, steps + 1):
            t = i / steps
            self.position = (sx + (x - sx) * t, sy + (y - sy) * t)
            await asyncio.sleep(duration / steps)

    async def wait(self, seconds: float) -> None:
        await asyncio.sleep(max(0.0, float(seconds)))

    def jump(self, height: float = 50.0) -> None:
        # Sem física real; apenas move para cima.
        x, y = self.position
        self.position = (x, y + float(height))
        self.on_ground = False

    def apply_force(self, fx: float, fy: float) -> None:
        vx, vy = self.velocity
        self.velocity = (vx + float(fx), vy + float(fy))

    def bounce_if_on_edge(self) -> None:
        x, y = self.position
        # bounds padrão (serão sobrepostos pela câmera)
        x = max(-180.0, min(180.0, x))
        y = max(-180.0, min(180.0, y))
        self.position = (x, y)

    def collide_world(self) -> bool:
        x, y = self.position
        return abs(x) > 180.0 or abs(y) > 180.0

    def collide_point(self, x: float, y: float) -> bool:
        sx, sy = self.position
        return abs(sx - x) <= self.fw / 2 and abs(sy - y) <= self.fh / 2

    def distance_to(self, target: "SpriteProxy | tuple[float, float]") -> float:
        if hasattr(target, "position"):
            tx, ty = target.position
        else:
            tx, ty = target[0], target[1]
        sx, sy = self.position
        return math.hypot(sx - tx, sy - ty)

    def look_at(self, target) -> None:
        if hasattr(target, "position"):
            tx, ty = target.position
        else:
            tx, ty = target[0], target[1]
        sx, sy = self.position
        dx, dy = tx - sx, ty - sy
        if dx == 0 and dy == 0:
            return
        self.rotation = math.degrees(math.atan2(dy, dx))

    async def show_speech(self, message: str, duration: float = 2.0) -> None:
        await asyncio.sleep(max(0.0, float(duration)))

    async def show_thought(self, message: str, duration: float = 2.0) -> None:
        await asyncio.sleep(max(0.0, float(duration)))

    async def ask(self, question: str) -> str:
        await asyncio.sleep(0.0)
        return ""

    def clone(self) -> "SpriteProxy":
        from copy import deepcopy
        return deepcopy(self)

    def delete(self) -> None:
        self.visible = False

    def set_animation(self, name: str) -> None:
        self.current_animation = name

    def loop_animation(self, on: bool = True) -> None:
        pass

    def play_sound(self, sound: Any) -> None:
        self.sound = sound

    def stop_all_sounds(self) -> None:
        self.sound = None

    def animate(self, on: bool = True) -> None:
        self._attrs_animate = bool(on)  # noqa: F841

    # ----- propriedades computadas (look at) --------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return f"SpriteProxy(name={self.name!r}, pos={self.position})"


# --- Stage -----------------------------------------------------------------
@dataclass
class Stage:
    """Palco: lista de sprites, sprite ativo, cena atual."""

    sprites: list[SpriteProxy] = field(default_factory=list)
    active: SpriteProxy | None = None
    scene_id: str = ""
    background: tuple[float, float, float, float] = (0.05, 0.05, 0.05, 1.0)
    width: float = 390.0
    height: float = 844.0

    def __post_init__(self) -> None:
        if not self.sprites:
            self.sprites = [SpriteProxy(name="Sprite1")]
        if self.active is None:
            self.active = self.sprites[0]

    def add_sprite(self, sprite: SpriteProxy) -> int:
        self.sprites.append(sprite)
        return len(self.sprites) - 1

    def set_active(self, sprite_id: int | str) -> None:
        if isinstance(sprite_id, int):
            if 0 <= sprite_id < len(self.sprites):
                self.active = self.sprites[sprite_id]
        elif isinstance(sprite_id, str):
            for s in self.sprites:
                if s.name == sprite_id:
                    self.active = s
                    return

    def broadcast(self, message: str) -> None:
        # Conectado ao Services.bus pelo make_ctx (ver wiring abaixo).
        pass


# --- RuntimeContext --------------------------------------------------------
@dataclass
class RuntimeContext:
    """Contexto passado para `BlockBehavior.run(ctx)`."""

    stage: Stage
    services: Services
    clock: float = 0.0
    timer: float = 0.0
    answer: str = ""
    variables: dict[str, Any] = field(default_factory=dict)

    # helpers convenientes para o executor -----------------------------
    @property
    def active_sprite(self) -> SpriteProxy | None:
        return self.stage.active


def make_ctx(*, screen_width: float = 390.0, screen_height: float = 844.0) -> RuntimeContext:
    """Constrói um RuntimeContext pronto para rodar blocos em testes."""
    services = Services()
    services.screen.width = float(screen_width)
    services.screen.height = float(screen_height)
    stage = Stage(width=services.screen.width, height=services.screen.height)
    return RuntimeContext(stage=stage, services=services)


__all__ = ["RuntimeContext", "SpriteProxy", "Stage", "make_ctx"]
