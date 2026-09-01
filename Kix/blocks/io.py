"""Blocos de I/O: sound + device + files."""

from Kix.block_engine import (
    BlockInput,
    BlockVisual,
    Group,
    KixBlock,
    SocketDef,
    SocketKind,
    Text,
)
from Kix.block_engine.behavior import BlockBehavior
from Kix.core.theme import CAT_DEVICE, CAT_FILES, CAT_SOUND


# ============================================================ Sound (6)
PLAY_SOUND = KixBlock(
    id="sound.play",
    name="Tocar som",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[Text("Tocar "), BlockInput("sound")])),
    inputs=[SocketDef("sound", SocketKind.SOUND)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.play_sound(self.sound)"),
    permissions={"sound"},
)

PLAY_SOUND_UNTIL_DONE = KixBlock(
    id="sound.play_until_done",
    name="Tocar até o fim",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[Text("Tocar "), BlockInput("sound"), Text(" até o fim")])),
    inputs=[SocketDef("sound", SocketKind.SOUND)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="await self.play_sound(self.sound, blocking=True)"),
    permissions={"sound"},
)

STOP_ALL_SOUNDS = KixBlock(
    id="sound.stop_all",
    name="Parar todos os sons",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[Text("Parar todos os sons")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="self.stop_all_sounds()"),
    permissions={"sound"},
)

SET_VOLUME = KixBlock(
    id="sound.set_volume",
    name="Definir volume",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[Text("Volume = "), BlockInput("volume"), Text(" %")])),
    inputs=[SocketDef("volume", SocketKind.NUMBER, default=100)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="audio.volume = self.volume / 100"),
    permissions={"sound"},
)

CHANGE_VOLUME = KixBlock(
    id="sound.change_volume",
    name="Mudar volume",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[Text("Mudar volume por "), BlockInput("delta"), Text(" %")])),
    inputs=[SocketDef("delta", SocketKind.NUMBER, default=-10)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="audio.volume += self.delta / 100"),
    permissions={"sound"},
)

MUTE = KixBlock(
    id="sound.mute",
    name="Silenciar",
    category="sound",
    color=CAT_SOUND,
    visual=BlockVisual(root=Group(children=[Text("Silenciar")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="audio.muted = True"),
    permissions={"sound"},
)


# ============================================================ Device (8)
VIBRATE = KixBlock(
    id="device.vibrate",
    name="Vibrar",
    category="device",
    color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("Vibrar por "), BlockInput("ms"), Text(" ms")])),
    inputs=[SocketDef("ms", SocketKind.NUMBER, default=200)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="device.vibrate(self.ms)"),
    permissions={"device"},
)

VIBRATE_LONG = KixBlock(
    id="device.vibrate_long",
    name="Vibração longa",
    category="device",
    color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("Vibrar por "), BlockInput("ms"), Text(" ms (longo)")])),
    inputs=[SocketDef("ms", SocketKind.NUMBER, default=800)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="device.vibrate_long(self.ms)"),
    permissions={"device"},
)

SET_BRIGHTNESS = KixBlock(
    id="device.set_brightness",
    name="Definir brilho",
    category="device",
    color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("Brilho = "), BlockInput("brightness"), Text(" %")])),
    inputs=[SocketDef("brightness", SocketKind.NUMBER, default=80)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="device.brightness = self.brightness / 100"),
    permissions={"device"},
)

BATTERY_LEVEL = KixBlock(
    id="device.battery",
    name="Bateria",
    category="device",
    color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("Nível da bateria (0-100)")])),
    inputs=[],
    outputs=[SocketDef("level", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return device.battery_level"),
    permissions={"device"},
)

SCREEN_ROTATION = KixBlock(
    id="device.rotation",
    name="Rotação da tela",
    category="device",
    color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("Rotação da tela: "), BlockInput("orientation")])),
    inputs=[SocketDef("orientation", SocketKind.STRING, default="portrait")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="device.orientation = self.orientation"),
    permissions={"device"},
)

GPS_LOCATION = KixBlock(
    id="device.gps",
    name="Localização GPS",
    category="device",
    color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("Localização atual (lat, lng)")])),
    inputs=[],
    outputs=[SocketDef("lat", SocketKind.NUMBER),
             SocketDef("lng", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return device.gps_location"),
    permissions={"gps"},
)

ACCELEROMETER_X = KixBlock(
    id="device.accel_x",
    name="Acelerômetro X",
    category="device",
    color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("Acelerômetro X")])),
    inputs=[],
    outputs=[SocketDef("x", SocketKind.NUMBER)],
    behavior=BlockBehavior(language="python", source="return device.accelerometer[0]"),
    permissions={"sensors"},
)

IS_MOBILE = KixBlock(
    id="device.is_mobile",
    name="É mobile?",
    category="device",
    color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("Rodando em celular?")])),
    inputs=[],
    outputs=[SocketDef("is_mobile", SocketKind.BOOLEAN)],
    behavior=BlockBehavior(language="python", source="return platform.is_mobile"),
    permissions={"device"},
)


# ============================================================ Files (6)
OPEN_PROJECT = KixBlock(
    id="files.open_project",
    name="Abrir projeto",
    category="files",
    color=CAT_FILES,
    visual=BlockVisual(root=Group(children=[Text("Abrir projeto "), BlockInput("name")])),
    inputs=[SocketDef("name", SocketKind.STRING, default="")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="projects.load(self.name)"),
    permissions={"storage"},
)

SAVE_PROJECT = KixBlock(
    id="files.save_project",
    name="Salvar projeto",
    category="files",
    color=CAT_FILES,
    visual=BlockVisual(root=Group(children=[Text("Salvar projeto")])),
    inputs=[],
    outputs=[],
    behavior=BlockBehavior(language="python", source="projects.save()"),
    permissions={"storage"},
)

EXPORT_PROJECT = KixBlock(
    id="files.export",
    name="Exportar projeto",
    category="files",
    color=CAT_FILES,
    visual=BlockVisual(root=Group(children=[Text("Exportar como "), BlockInput("format")])),
    inputs=[SocketDef("format", SocketKind.STRING, default="kix")],
    outputs=[],
    behavior=BlockBehavior(language="python", source="projects.export(self.format)"),
    permissions={"storage"},
)

IMPORT_BLOCKS = KixBlock(
    id="files.import_blocks",
    name="Importar blocos",
    category="files",
    color=CAT_FILES,
    visual=BlockVisual(root=Group(children=[Text("Importar "), BlockInput("path")])),
    inputs=[SocketDef("path", SocketKind.FILE)],
    outputs=[],
    behavior=BlockBehavior(language="python", source="blocks.import_from(self.path)"),
    permissions={"storage"},
)

LIST_FILES = KixBlock(
    id="files.list",
    name="Listar arquivos",
    category="files",
    color=CAT_FILES,
    visual=BlockVisual(root=Group(children=[Text("Arquivos em "), BlockInput("folder")])),
    inputs=[SocketDef("folder", SocketKind.STRING, default="/")],
    outputs=[SocketDef("files", SocketKind.STRING)],
    behavior=BlockBehavior(language="python", source="return os.listdir(self.folder)"),
    permissions={"storage"},
)

READ_TEXT = KixBlock(
    id="files.read_text",
    name="Ler arquivo de texto",
    category="files",
    color=CAT_FILES,
    visual=BlockVisual(root=Group(children=[Text("Ler "), BlockInput("path")])),
    inputs=[SocketDef("path", SocketKind.FILE)],
    outputs=[SocketDef("content", SocketKind.STRING)],
    behavior=BlockBehavior(language="python", source="return open(self.path).read()"),
    permissions={"storage"},
)


# --- M3.3: device + platform faltando (5) --------------------------------
ACCELEROMETER_Y = KixBlock(
    id="device.accel_y", name="aceleração y", category="device",
    color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("aceleração y")])),
    inputs=[], outputs=[SocketDef("y", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return device.accel[1]"),
    permissions={"device"},
)
ACCELEROMETER_Z = KixBlock(
    id="device.accel_z", name="aceleração z", category="device",
    color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("aceleração z")])),
    inputs=[], outputs=[SocketDef("z", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return device.accel[2]"),
    permissions={"device"},
)
CLIPBOARD_TEXT = KixBlock(
    id="device.clipboard_text", name="texto da área de transferência",
    category="device", color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("texto da área de transferência")])),
    inputs=[], outputs=[SocketDef("text", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return device.clipboard_text"),
    permissions={"device"},
)
KEYBOARD_HEIGHT = KixBlock(
    id="device.keyboard_height", name="altura do teclado",
    category="device", color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("altura do teclado")])),
    inputs=[], outputs=[SocketDef("height", SocketKind.NUMBER)],
    behavior=BlockBehavior("python", "return device.keyboard_height"),
    permissions={"device"},
)
PLATFORM_ARCHITECTURE = KixBlock(
    id="platform.architecture", name="arquitetura", category="device",
    color=CAT_DEVICE,
    visual=BlockVisual(root=Group(children=[Text("arquitetura")])),
    inputs=[], outputs=[SocketDef("arch", SocketKind.STRING)],
    behavior=BlockBehavior("python", "return platform.architecture"),
    permissions={"device"},
)


IO = (PLAY_SOUND, PLAY_SOUND_UNTIL_DONE, STOP_ALL_SOUNDS,
      SET_VOLUME, CHANGE_VOLUME, MUTE,
      VIBRATE, VIBRATE_LONG, SET_BRIGHTNESS, BATTERY_LEVEL,
      SCREEN_ROTATION, GPS_LOCATION, ACCELEROMETER_X, IS_MOBILE,
      OPEN_PROJECT, SAVE_PROJECT, EXPORT_PROJECT, IMPORT_BLOCKS,
      LIST_FILES, READ_TEXT,
      ACCELEROMETER_Y, ACCELEROMETER_Z, CLIPBOARD_TEXT, KEYBOARD_HEIGHT,
      PLATFORM_ARCHITECTURE)

assert len(IO) == 25, f"esperado 25, obtido {len(IO)}"