"""Container de serviços do runtime.

Cada bloco referencia um conjunto de globais (`camera`, `audio`,
`tilemap`, `device`, `network`, …). Em vez de poluir o namespace global
do Python, mantemos `Services` como um container de proxies. O executor
expõe os serviços no namespace plano da execução (junto com `math`,
`random`, etc.).

Em M3 (MVP) cada serviço é um stub que:
- aceita leituras e gravações de atributos (estado em memória);
- oferece métodos async como `await camera.shake(...)` que retornam
  após `asyncio.sleep(...)` ou levantam `NotImplementedError` honesto
  quando o driver real ainda não está cabeado.

Não mentimos sobre o que está implementado — drivers reais (Kivy,
Android, network) entram em marcos seguintes.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any


# --- Helpers ---------------------------------------------------------------
def _not_implemented(driver: str) -> None:
    raise NotImplementedError(
        f"Driver '{driver}' fora do MVP M3. Veja plans/ancient-giggling-clarke.md."
    )


@dataclass
class _ServiceBase:
    """Base com __getattr__/__setattr__ permissivos para suportar state.

    Filhos sobrescrevem métodos que devem ter comportamento real; o resto
    cai no dict dinâmico `_attrs`. Para atributos que são campos do
    dataclass (declared in class body), escrita vai para o instance dict
    (sobrescrevendo o default); para atributos dinâmicos, vai para `_attrs`.
    """

    name: str = "service"

    # Campos declarados no dataclass — vão para o instance dict.
    _DATACLASS_FIELDS: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        object.__setattr__(self, "_attrs", {})

    def __getattr__(self, item: str) -> Any:
        if item.startswith("_"):
            raise AttributeError(item)
        attrs = object.__getattribute__(self, "_attrs")
        if item in attrs:
            return attrs[item]
        return None

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith("_") or key in {"name"}:
            object.__setattr__(self, key, value)
            return
        try:
            attrs = object.__getattribute__(self, "_attrs")
        except AttributeError:
            object.__setattr__(self, key, value)
            return
        # Se for campo do dataclass, sobrescreve no instance dict.
        # Caso contrário, vai para `_attrs` (atributo dinâmico).
        fields = type(self).__dataclass_fields__ if hasattr(type(self), "__dataclass_fields__") else {}
        if key in fields:
            object.__setattr__(self, key, value)
        else:
            attrs[key] = value


# --- Stage / camera / motion ----------------------------------------------
@dataclass
class CameraProxy(_ServiceBase):
    name: str = "camera"

    async def shake(self, intensity: float = 1.0, duration: float = 0.3) -> None:
        await asyncio.sleep(max(0.0, float(duration)))

    def follow(self, target: Any) -> None:
        self._attrs["follow"] = target

    def unfollow(self) -> None:
        self._attrs.pop("follow", None)

    async def goto(self, x: float, y: float, duration: float = 0.0) -> None:
        self._attrs["position"] = (float(x), float(y))
        if duration > 0:
            await asyncio.sleep(duration)

    def limit(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self._attrs["bounds"] = (float(x1), float(y1), float(x2), float(y2))

    def reset(self) -> None:
        self._attrs.clear()

    def stop(self) -> None:
        self._attrs.pop("follow", None)

    def zoom(self, factor: float) -> None:
        self._attrs["zoom"] = float(factor)


@dataclass
class InputProxy(_ServiceBase):
    name: str = "input"
    # Catroid usa `input.mouse[0/1]` — expomos como tupla
    mouse: tuple[float, float] = (0.0, 0.0)


# --- Audio -----------------------------------------------------------------
@dataclass
class MicProxy:
    frequency: float = 0.0
    level: float = 0.0


@dataclass
class AudioProxy(_ServiceBase):
    name: str = "audio"
    mic: MicProxy = field(default_factory=MicProxy)

    def play_pitched(self, sound: Any, pitch: float = 1.0) -> None:
        # No-op honesto
        return None

    def set_eq(self, band: int, gain: float) -> None:
        eq = self._attrs.setdefault("eq", [0.0] * 10)
        if 0 <= band < len(eq):
            eq[band] = float(gain)

    def set_pan(self, pan: float) -> None:
        self._attrs["pan"] = float(pan)

    async def fade_in(self, sound: Any, duration: float = 1.0) -> None:
        await asyncio.sleep(max(0.0, float(duration)))

    async def fade_out(self, sound: Any, duration: float = 1.0) -> None:
        await asyncio.sleep(max(0.0, float(duration)))


# --- Joystick --------------------------------------------------------------
@dataclass
class JoystickProxy:
    """Um joystick virtual; o `Services` tem um `default` e uma fábrica."""

    direction: tuple[float, float] = (0.0, 0.0)
    magnitude: float = 0.0
    angle: float = 0.0
    is_active: bool = False
    deadzone: float = 0.1

    def update(self, x: float, y: float) -> None:
        import math
        self.direction = (float(x), float(y))
        self.magnitude = math.hypot(x, y)
        self.angle = math.degrees(math.atan2(y, x)) if self.magnitude > 0 else 0.0
        self.is_active = self.magnitude > self.deadzone


# --- Tilemap / Layers / Sheet / Pen / Shader -------------------------------
@dataclass
class TilemapProxy(_ServiceBase):
    name: str = "tilemap"

    def load(self, path: str) -> None:
        self._attrs["path"] = path

    def save(self, path: str) -> None:
        self._attrs["saved_to"] = path

    def clear(self) -> None:
        self._attrs["tiles"] = {}

    def fill(self, tile_id: int, region: tuple[int, int, int, int]) -> None:
        self._attrs["fill"] = (tile_id, region)

    def set_tile(self, x: int, y: int, tile_id: int) -> None:
        tiles = self._attrs.setdefault("tiles", {})
        tiles[(int(x), int(y))] = int(tile_id)

    def tile_at(self, x: int, y: int) -> int:
        return self._attrs.get("tiles", {}).get((int(x), int(y)), 0)

    def is_solid(self, x: int, y: int) -> bool:
        return self.tile_at(x, y) != 0

    def collides(self, x: float, y: float) -> bool:
        return self.is_solid(int(x), int(y))


@dataclass
class LayersProxy(_ServiceBase):
    """Gerencia layers da cena (por nome e categoria).

    Categorias válidas: "ui", "background", "player", "enemy", "other".
    Layers são dicts internos; o engine expõe `layers[name]` para leitura.
    """

    name: str = "layers"
    VALID_CATEGORIES = ("ui", "background", "player", "enemy", "other")

    # --- internos -------------------------------------------------------
    def _layers(self) -> list[dict]:
        return self._attrs.setdefault("layers", [])

    def _find_index(self, name: str) -> int:
        for i, lyr in enumerate(self._layers()):
            if lyr.get("name") == name:
                return i
        return -1

    def _get(self, name: str) -> dict | None:
        idx = self._find_index(name)
        if idx < 0:
            return None
        return self._layers()[idx]

    # --- API pública ----------------------------------------------------
    def create(self, name: str, category: str = "other") -> bool:
        """Cria layer nova. Retorna False se já existe ou categoria inválida."""
        if category not in self.VALID_CATEGORIES:
            category = "other"
        if self._find_index(name) >= 0:
            return False
        layers = self._layers()
        z = max((l.get("z", 0) for l in layers), default=-1) + 1
        layers.append({
            "name": name,
            "category": category,
            "z": z,
            "visible": True,
            "collidable": True,
            "shader": "",
            "objects": [],
        })
        return True

    def remove(self, name: str) -> bool:
        for i, lyr in enumerate(self._layers()):
            if lyr.get("name") == name:
                self._layers().pop(i)
                return True
        return False

    def exists(self, name: str) -> bool:
        return self._find_index(name) >= 0

    def count(self) -> int:
        return len(self._layers())

    def current(self) -> str:
        return str(self._attrs.get("current", ""))

    def switch(self, name: str) -> None:
        if self._find_index(name) >= 0:
            self._attrs["current"] = name

    def set_z(self, name: str, z: int) -> None:
        lyr = self._get(name)
        if lyr is not None:
            lyr["z"] = int(z)

    def set_category(self, name: str, category: str) -> None:
        if category not in self.VALID_CATEGORIES:
            category = "other"
        lyr = self._get(name)
        if lyr is not None:
            lyr["category"] = category

    def show(self, name: str) -> None:
        lyr = self._get(name)
        if lyr is not None:
            lyr["visible"] = True

    def hide(self, name: str) -> None:
        lyr = self._get(name)
        if lyr is not None:
            lyr["visible"] = False

    def is_visible(self, name: str) -> bool:
        lyr = self._get(name)
        return bool(lyr.get("visible", True)) if lyr else False

    def set_collidable(self, name: str, collidable: bool) -> None:
        lyr = self._get(name)
        if lyr is not None:
            lyr["collidable"] = bool(collidable)

    def is_collidable(self, name: str) -> bool:
        lyr = self._get(name)
        return bool(lyr.get("collidable", True)) if lyr else False

    def set_shader(self, name: str, shader: str) -> None:
        lyr = self._get(name)
        if lyr is not None:
            lyr["shader"] = str(shader)

    def clear_shader(self, name: str) -> None:
        self.set_shader(name, "")

    def apply_shader_except(self, shader: str, except_name: str) -> None:
        """Aplica shader a todas as layers exceto a de nome `except_name`."""
        for lyr in self._layers():
            if lyr.get("name") != except_name:
                lyr["shader"] = str(shader)

    def add_object(self, layer_name: str, object_id: str) -> bool:
        lyr = self._get(layer_name)
        if lyr is None:
            return False
        if object_id not in lyr["objects"]:
            lyr["objects"].append(object_id)
        return True

    def remove_object(self, layer_name: str, object_id: str) -> bool:
        lyr = self._get(layer_name)
        if lyr is None:
            return False
        if object_id in lyr["objects"]:
            lyr["objects"].remove(object_id)
            return True
        return False

    def object_count(self, name: str) -> int:
        lyr = self._get(name)
        return len(lyr.get("objects", [])) if lyr else 0

    def contains_object(self, name: str, object_id: str) -> bool:
        lyr = self._get(name)
        return object_id in (lyr.get("objects", []) if lyr else [])

    def clear(self, name: str) -> bool:
        lyr = self._get(name)
        if lyr is None:
            return False
        lyr["objects"] = []
        return True

    def swap(self, name_a: str, name_b: str) -> bool:
        idx_a = self._find_index(name_a)
        idx_b = self._find_index(name_b)
        if idx_a < 0 or idx_b < 0:
            return False
        layers = self._layers()
        # troca posição na lista E os valores de z (para que z_index reflita a nova ordem)
        layers[idx_a], layers[idx_b] = layers[idx_b], layers[idx_a]
        z_a = layers[idx_a].get("z", 0)
        z_b = layers[idx_b].get("z", 0)
        layers[idx_a]["z"] = z_b
        layers[idx_b]["z"] = z_a
        return True

    def above(self, name: str, other_name: str) -> None:
        """Move `name` para imediatamente acima de `other_name` (z maior)."""
        idx = self._find_index(name)
        other_idx = self._find_index(other_name)
        if idx < 0 or other_idx < 0:
            return
        lyr = self._layers()[idx]
        other = self._layers()[other_idx]
        lyr["z"] = other.get("z", 0) + 1

    def z_index(self, name: str) -> int:
        lyr = self._get(name)
        return int(lyr.get("z", 0)) if lyr else -1

    # --- compatibilidade com API antiga baseada em id ------------------
    def create_index(self, name: str) -> int:
        layers = self._attrs.setdefault("layers", [])
        lid = len(layers)
        layers.append({"name": name, "z": lid, "visible": True})
        return lid

    def set_z_by_id(self, layer_id: int, z: int) -> None:
        layers = self._layers()
        if 0 <= layer_id < len(layers):
            layers[layer_id]["z"] = int(z)

    def show_by_id(self, layer_id: int) -> None:
        layers = self._layers()
        if 0 <= layer_id < len(layers):
            layers[layer_id]["visible"] = True

    def hide_by_id(self, layer_id: int) -> None:
        layers = self._layers()
        if 0 <= layer_id < len(layers):
            layers[layer_id]["visible"] = False

    def forward(self, layer_id: int) -> None:
        layers = self._layers()
        if 0 <= layer_id < len(layers):
            layers[layer_id]["z"] = layers[layer_id].get("z", 0) + 1

    def backward(self, layer_id: int) -> None:
        layers = self._layers()
        if 0 <= layer_id < len(layers):
            layers[layer_id]["z"] = layers[layer_id].get("z", 0) - 1


@dataclass
class SpritesheetProxy(_ServiceBase):
    name: str = "sheet"

    def load(self, path: str) -> None:
        self._attrs["path"] = path

    def set_animation(self, name: str) -> None:
        self._attrs["animation"] = name

    def current(self) -> str:
        return self._attrs.get("animation", "")

    def loop(self, on: bool = True) -> None:
        self._attrs["loop"] = bool(on)

    def pause(self) -> None:
        self._attrs["paused"] = True

    def resume(self) -> None:
        self._attrs["paused"] = False

    def next_frame(self) -> None:
        self._attrs["frame"] = int(self._attrs.get("frame", 0)) + 1

    def prev_frame(self) -> None:
        self._attrs["frame"] = max(0, int(self._attrs.get("frame", 0)) - 1)


@dataclass
class PenProxy(_ServiceBase):
    name: str = "pen"

    def down(self) -> None:
        self._attrs["down"] = True

    def up(self) -> None:
        self._attrs["down"] = False

    def clear(self) -> None:
        self._attrs.clear()

    def stamp(self) -> None:
        self._attrs["stamps"] = self._attrs.get("stamps", 0) + 1

    def change_color(self, amount: float) -> None:
        self._attrs["hue_shift"] = float(amount)


@dataclass
class ShaderProxy(_ServiceBase):
    name: str = "shader"

    def blur(self, radius: float = 1.0) -> None:
        self._attrs["blur"] = float(radius)

    def pixelate(self, size: int = 4) -> None:
        self._attrs["pixelate"] = int(size)

    def glow(self, intensity: float = 1.0) -> None:
        self._attrs["glow"] = float(intensity)

    def vignette(self, intensity: float = 0.5) -> None:
        self._attrs["vignette"] = float(intensity)

    def grayscale(self) -> None:
        self._attrs["grayscale"] = True

    def sepia(self) -> None:
        self._attrs["sepia"] = True

    def sharpen(self) -> None:
        self._attrs["sharpen"] = True

    def reset(self) -> None:
        self._attrs.clear()


# --- Physics ---------------------------------------------------------------
@dataclass
class PhysicsProxy(_ServiceBase):
    name: str = "physics"

    def raycast(self, x1: float, y1: float, x2: float, y2: float) -> tuple[bool, float]:
        return (False, 0.0)

    async def add_force(self, fx: float, fy: float) -> None:
        return None


# --- Scenes / Storage / UI / Particles / Notif / AR / VR ------------------
@dataclass
class ScenesProxy(_ServiceBase):
    name: str = "scenes"
    current_id: str = ""
    count: int = 0

    def switch(self, scene_id: str) -> None:
        self.current_id = scene_id

    def current(self) -> str:
        return self.current_id


@dataclass
class StorageProxy(_ServiceBase):
    name: str = "storage"
    store: dict[str, Any] = field(default_factory=dict)

    # interface dict-like para os blocos usarem `storage[key]`, `len(storage)`, etc.
    def __getitem__(self, key: str) -> Any:
        return self.store[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.store[key] = value

    def __delitem__(self, key: str) -> None:
        del self.store[key]

    def __contains__(self, key: str) -> bool:
        return key in self.store

    def __iter__(self):
        return iter(self.store)

    def __len__(self) -> int:
        return len(self.store)

    def keys(self):
        return self.store.keys()

    def values(self):
        return self.store.values()

    def items(self):
        return self.store.items()

    def get(self, key: str, default: Any = None) -> Any:
        return self.store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.store[key] = value

    def has(self, key: str) -> bool:
        return key in self.store

    def pop(self, key: str, default: Any = None) -> Any:
        return self.store.pop(key, default)

    def clear(self) -> None:
        self.store.clear()

    def delete(self, key: str) -> None:
        self.store.pop(key, None)


@dataclass
class UiProxy(_ServiceBase):
    name: str = "ui"
    widgets: dict[int, dict[str, Any]] = field(default_factory=dict)

    def create_button(self, label: str, x: float, y: float) -> int:
        wid = len(self.widgets)
        self.widgets[wid] = {"type": "button", "label": label, "x": x, "y": y}
        return wid

    def create_text(self, text: str, x: float, y: float) -> int:
        wid = len(self.widgets)
        self.widgets[wid] = {"type": "text", "text": text, "x": x, "y": y}
        return wid

    def create_slider(self, min_v: float, max_v: float, value: float) -> int:
        wid = len(self.widgets)
        self.widgets[wid] = {"type": "slider", "min": min_v, "max": max_v, "value": value}
        return wid

    def create_progress(self, value: float, max_v: float = 1.0) -> int:
        wid = len(self.widgets)
        self.widgets[wid] = {"type": "progress", "value": value, "max": max_v}
        return wid

    def set_text(self, wid: int, text: str) -> None:
        if wid in self.widgets:
            self.widgets[wid]["text"] = text

    def set_button_label(self, wid: int, label: str) -> None:
        if wid in self.widgets:
            self.widgets[wid]["label"] = label

    def set_progress_value(self, wid: int, value: float) -> None:
        if wid in self.widgets:
            self.widgets[wid]["value"] = value

    def slider_value(self, wid: int) -> float:
        return float(self.widgets.get(wid, {}).get("value", 0.0))

    def button_clicked(self, wid: int) -> bool:
        return bool(self.widgets.get(wid, {}).get("clicked", False))

    def hide(self, wid: int) -> None:
        if wid in self.widgets:
            self.widgets[wid]["visible"] = False

    def dialog(self, title: str, message: str) -> None:
        self._attrs["last_dialog"] = (title, message)

    def toast(self, message: str) -> None:
        self._attrs["last_toast"] = message

    def alert(self, title: str, message: str) -> None:
        self.dialog(title, message)


@dataclass
class ParticlesProxy(_ServiceBase):
    name: str = "particles"

    def emit(self, x: float, y: float, count: int = 10) -> None:
        self._attrs.setdefault("emitted", []).append((x, y, count))


@dataclass
class NotificationsProxy(_ServiceBase):
    name: str = "notif"

    def toast(self, message: str) -> None:
        self._attrs["last_toast"] = message

    def alert(self, title: str, message: str) -> None:
        self._attrs["last_alert"] = (title, message)

    def dialog(self, title: str, message: str) -> None:
        self.alert(title, message)


@dataclass
class ArvrProxy(_ServiceBase):
    name: str = "arvr"

    def start(self) -> None:
        self._attrs["started"] = True

    def plane_detected(self) -> bool:
        return bool(self._attrs.get("plane_detected", False))

    def hit_test(self, x: float, y: float) -> tuple[bool, float, float]:
        return (False, 0.0, 0.0)


# --- Device / Screen / Platform / Engine -----------------------------------
@dataclass
class DeviceProxy(_ServiceBase):
    name: str = "device"
    accel: tuple[float, float, float] = (0.0, 0.0, 0.0)
    battery_level: float = 1.0
    gps_location: tuple[float, float] = (0.0, 0.0)
    is_mobile: bool = False
    orientation: str = "portrait"
    rotation: float = 0.0
    clipboard_text: str = ""
    keyboard_height: float = 0.0
    # sensores estendidos (stubs honestos — bridge Android substitui depois)
    gps: tuple[float, float, float] = (0.0, 0.0, 0.0)            # lat, lng, alt
    gps_accuracy: float = 0.0
    compass: float = 0.0                                          # heading em graus
    tilt: tuple[float, float] = (0.0, 0.0)                        # x, y (-1..1)
    light: float = 0.0
    proximity: float = 0.0
    noise: float = 0.0
    temperature: float = 20.0
    humidity: float = 0.0
    pressure: float = 1013.25
    nfc_last_tag: str = ""
    last_speech: str = ""

    def vibrate(self, ms: int = 100) -> None:
        self._attrs["last_vibrate_ms"] = int(ms)

    def vibrate_long(self) -> None:
        self.vibrate(500)

    def vibrate_pattern(self, pattern: list[int]) -> None:
        self._attrs["last_vibrate_pattern"] = list(pattern)

    def set_brightness(self, value: float) -> None:
        self._attrs["brightness"] = float(value)


@dataclass
class ScreenProxy(_ServiceBase):
    name: str = "screen"
    width: float = 390.0
    height: float = 844.0

    def color_at(self, x: float, y: float) -> str:
        return "#000000"

    def color_equal_with_tolerance(self, a: str, b: str, tolerance: float) -> bool:
        # comparação simples de hex
        return a.lower() == b.lower()


@dataclass
class PlatformProxy(_ServiceBase):
    name: str = "platform"
    architecture: str = "x86_64"
    os: str = "linux"


@dataclass
class EngineProxy(_ServiceBase):
    name: str = "engine"
    fps: float = 60.0


# --- Network / HTTP / TCP / WS / UDP ---------------------------------------
class NetworkNotWired(NotImplementedError):
    """Driver de rede não cabeado no MVP M3. Não é stub silencioso."""


@dataclass
class HttpProxy:
    async def get(self, url: str, headers: dict | None = None) -> dict:
        raise NetworkNotWired("http.get")

    async def post(self, url: str, body: Any = None, headers: dict | None = None) -> dict:
        raise NetworkNotWired("http.post")

    async def put(self, url: str, body: Any = None, headers: dict | None = None) -> dict:
        raise NetworkNotWired("http.put")

    async def delete(self, url: str, headers: dict | None = None) -> dict:
        raise NetworkNotWired("http.delete")


@dataclass
class TcpProxy:
    async def connect(self, host: str, port: int) -> Any:
        raise NetworkNotWired("tcp.connect")

    async def send(self, conn: Any, data: bytes) -> None:
        raise NetworkNotWired("tcp.send")

    async def recv(self, conn: Any, nbytes: int) -> bytes:
        raise NetworkNotWired("tcp.recv")

    def close(self, conn: Any) -> None:
        return None


@dataclass
class WsProxy:
    async def connect(self, url: str) -> Any:
        raise NetworkNotWired("ws.connect")

    async def send(self, ws: Any, data: str) -> None:
        raise NetworkNotWired("ws.send")

    async def recv(self, ws: Any) -> str:
        raise NetworkNotWired("ws.recv")


@dataclass
class UdpProxy:
    async def sendto(self, host: str, port: int, data: bytes) -> None:
        raise NetworkNotWired("udp.sendto")

    async def recvfrom(self, timeout: float = 1.0) -> tuple[bytes, tuple[str, int]]:
        raise NetworkNotWired("udp.recvfrom")


@dataclass
class NetworkProxy(_ServiceBase):
    name: str = "network"
    is_connected: bool = False
    local_ip: str = "127.0.0.1"
    local_port: int = 0


# --- Broadcast (sinais globais) --------------------------------------------
@dataclass
class BroadcastBus:
    """Registrador de broadcasts. Listeners reais entram em marco futuro."""

    history: list[str] = field(default_factory=list)
    waiters: dict[str, list[asyncio.Future]] = field(default_factory=dict)
    listeners: dict[str, list] = field(default_factory=dict)

    def emit(self, message: str) -> None:
        self.history.append(message)
        for fut in self.waiters.pop(message, []):
            if not fut.done():
                fut.set_result(True)

    async def emit_and_wait(self, message: str) -> None:
        self.emit(message)
        loop = asyncio.get_event_loop()
        fut = loop.create_future()
        self.waiters.setdefault(message, []).append(fut)
        await fut

    def when(self, message: str, handler) -> None:
        """Registra um handler para a mensagem. Disparo imediato em M5 (síncrono)."""
        self.listeners.setdefault(message, []).append(handler)
        try:
            handler()
        except Exception:
            pass


# --- Hardware (Lego / Arduino / Makey) -----------------------------------
@dataclass
class NxtProxy(_ServiceBase):
    """Lego NXT (Bluetooth). Drivers reais plugados em runtime."""
    name: str = "nxt"
    connected: bool = False
    address: str = ""

    def connect(self, address: str) -> None:
        self.address = address
        self._attrs["last_connect"] = address
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def motor(self, port: str, speed: float, duration: float) -> None:
        self._attrs["last_motor"] = (port, float(speed), float(duration))

    def touch(self, port: str) -> bool:
        return bool(self._attrs.get(f"touch_{port}", False))

    def sound(self, port: str) -> float:
        return float(self._attrs.get(f"sound_{port}", 0.0))

    def light(self, port: str) -> float:
        return float(self._attrs.get(f"light_{port}", 0.0))

    def ultrasonic(self, port: str) -> float:
        return float(self._attrs.get(f"ultra_{port}", 0.0))

    def play_tone(self, frequency: float, duration_ms: float) -> None:
        self._attrs["last_tone"] = (float(frequency), float(duration_ms))


@dataclass
class ArduinoProxy(_ServiceBase):
    """Arduino (USB/Bluetooth). Drivers reais plugados em runtime."""
    name: str = "arduino"
    connected: bool = False
    port: str = ""

    def connect(self, port: str) -> None:
        self.port = port
        self._attrs["last_connect"] = port
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def digital_write(self, pin: int, value: bool) -> None:
        self._attrs[f"d_{int(pin)}"] = bool(value)

    def digital_read(self, pin: int) -> bool:
        return bool(self._attrs.get(f"d_{int(pin)}", False))

    def analog_write(self, pin: int, value: int) -> None:
        self._attrs[f"a_{int(pin)}"] = int(value)

    def analog_read(self, pin: int) -> float:
        return float(self._attrs.get(f"a_{int(pin)}", 0))


@dataclass
class MakeyProxy(_ServiceBase):
    """Makey-Makey (USB HID). Driver plugado em runtime."""
    name: str = "makey"
    connected: bool = False

    def connect(self) -> None:
        self.connected = True

    def is_pressed(self, key: str) -> bool:
        return bool(self._attrs.get(f"makey_{key.upper()}", False))


@dataclass
class TouchProxy(_ServiceBase):
    """Gestos multitouch: o Kivy injeta eventos aqui a partir do Widget root."""
    name: str = "touch"
    last_x: float = 0.0
    last_y: float = 0.0
    is_touched: bool = False
    tap_count: int = 0
    swipe: str = ""                # "left" | "right" | "up" | "down" | ""

    def feed_touch(self, x: float, y: float) -> None:
        self.last_x = float(x)
        self.last_y = float(y)
        self.is_touched = True
        self._attrs["last_touch_pos"] = (float(x), float(y))

    def feed_release(self) -> None:
        self.is_touched = False

    def feed_swipe(self, direction: str) -> None:
        self.swipe = direction


# --- Services (container final) -------------------------------------------
@dataclass
class Services:
    """Container de todos os proxies. Criado pelo `make_ctx()`."""

    camera: CameraProxy = field(default_factory=CameraProxy)
    input: InputProxy = field(default_factory=InputProxy)
    audio: AudioProxy = field(default_factory=AudioProxy)
    joystick: JoystickProxy = field(default_factory=JoystickProxy)
    tilemap: TilemapProxy = field(default_factory=TilemapProxy)
    layers: LayersProxy = field(default_factory=LayersProxy)
    sheet: SpritesheetProxy = field(default_factory=SpritesheetProxy)
    pen: PenProxy = field(default_factory=PenProxy)
    shader: ShaderProxy = field(default_factory=ShaderProxy)
    physics: PhysicsProxy = field(default_factory=PhysicsProxy)
    scenes: ScenesProxy = field(default_factory=ScenesProxy)
    storage: StorageProxy = field(default_factory=StorageProxy)
    ui: UiProxy = field(default_factory=UiProxy)
    particles: ParticlesProxy = field(default_factory=ParticlesProxy)
    notif: NotificationsProxy = field(default_factory=NotificationsProxy)
    arvr: ArvrProxy = field(default_factory=ArvrProxy)
    device: DeviceProxy = field(default_factory=DeviceProxy)
    screen: ScreenProxy = field(default_factory=ScreenProxy)
    platform: PlatformProxy = field(default_factory=PlatformProxy)
    engine: EngineProxy = field(default_factory=EngineProxy)
    network: NetworkProxy = field(default_factory=NetworkProxy)
    http: HttpProxy = field(default_factory=HttpProxy)
    tcp: TcpProxy = field(default_factory=TcpProxy)
    ws: WsProxy = field(default_factory=WsProxy)
    udp: UdpProxy = field(default_factory=UdpProxy)
    bus: BroadcastBus = field(default_factory=BroadcastBus)
    nxt: NxtProxy = field(default_factory=NxtProxy)
    arduino: ArduinoProxy = field(default_factory=ArduinoProxy)
    makey: MakeyProxy = field(default_factory=MakeyProxy)
    touch: TouchProxy = field(default_factory=TouchProxy)


# --- Helpers de broadcast expostos como funções no namespace -------------
def _broadcast(services: Services, message: str) -> None:
    services.bus.emit(message)


async def _broadcast_and_wait(services: Services, message: str) -> None:
    await services.bus.emit_and_wait(message)


def _joystick_factory(services: Services) -> JoystickProxy:
    """Cria um joystick virtual novo; o principal vive em `services.joystick`."""
    return JoystickProxy()


def flat_namespace(services: Services) -> dict[str, Any]:
    """Constrói o namespace plano usado pelo executor para cada bloco."""
    return {
        # engines / proxies
        "camera": services.camera,
        "input": services.input,
        "audio": services.audio,
        "joystick": services.joystick,
        "joystick_factory": lambda: _joystick_factory(services),
        "tilemap": services.tilemap,
        "layers": services.layers,
        "sheet": services.sheet,
        "pen": services.pen,
        "shader": services.shader,
        "physics": services.physics,
        "scenes": services.scenes,
        "scene": services.scenes,           # alias usado por algumas fontes
        "storage": services.storage,
        "ui": services.ui,
        "particles": services.particles,
        "notif": services.notif,
        "arvr": services.arvr,
        "device": services.device,
        "screen": services.screen,
        "platform": services.platform,
        "engine": services.engine,
        "network": services.network,
        "http": services.http,
        "tcp": services.tcp,
        "ws": services.ws,
        "udp": services.udp,
        "nxt": services.nxt,
        "arduino": services.arduino,
        "makey": services.makey,
        "touch": services.touch,
        # broadcast helpers
        "broadcast": lambda msg: _broadcast(services, msg),
        "broadcast_and_wait": lambda msg: _broadcast_and_wait(services, msg),
    }
