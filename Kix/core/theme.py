"""Design tokens do Kix.

Fonte única de verdade para cores, espaçamento, raios e tipografia.
Valores RGBA no formato aceito pelo Kivy (0.0 a 1.0).
"""

# --- Ações / destaque -------------------------------------------------------
EMERALD = (0.063, 0.725, 0.506, 1)            # #10B981
EMERALD_PRESSED = (0.050, 0.580, 0.405, 1)    # versão mais escura para :state=down

# --- Superfícies (escala grafite) -------------------------------------------
BG = (0.051, 0.051, 0.055, 1)                 # #0D0D0E  fundo da janela
SURFACE_1 = (0.071, 0.071, 0.078, 1)          # #121214  app bar
SURFACE_2 = (0.086, 0.086, 0.094, 1)          # #161618  card primário
SURFACE_3 = (0.110, 0.110, 0.122, 1)          # #1C1C1F  card secundário / hover
SURFACE_4 = (0.141, 0.141, 0.157, 1)          # #242428  divisores sutis

# --- Texto ------------------------------------------------------------------
WHITE = (1, 1, 1, 1)
TEXT_HIGH = (0.93, 0.93, 0.95, 1)             # títulos
TEXT_MED = (0.70, 0.70, 0.74, 1)              # corpo
TEXT_LOW = (0.45, 0.45, 0.50, 1)              # meta

# --- Paleta por categoria (Catroid-inspired) -------------------------------
# Cada categoria tem um tom; blocos embutidos referenciam estes.
CAT_MOTION = (0.20, 0.55, 0.85, 1)
CAT_LOOKS = (0.45, 0.75, 0.45, 1)
CAT_SOUND = (0.65, 0.40, 0.85, 1)
CAT_PEN = (0.35, 0.60, 0.35, 1)
CAT_CONTROL = (0.95, 0.65, 0.35, 1)
CAT_EVENT = (0.90, 0.45, 0.20, 1)
CAT_DATA = (0.95, 0.45, 0.55, 1)
CAT_DEVICE = (0.65, 0.55, 0.20, 1)
CAT_FILES = (0.85, 0.70, 0.30, 1)
CAT_USER = (0.30, 0.35, 0.75, 1)
CAT_LIBS = (0.95, 0.55, 0.85, 1)
CAT_CAMERA = (0.40, 0.70, 0.90, 1)
CAT_NETWORK = (0.35, 0.60, 0.80, 1)
CAT_LAYERS = (0.55, 0.55, 0.65, 1)
CAT_SHADERS = (0.75, 0.50, 0.85, 1)
CAT_UI = (0.20, 0.55, 0.55, 1)
CAT_TILEMAP = (0.55, 0.75, 0.40, 1)
CAT_SPRITESHEET = (0.85, 0.55, 0.35, 1)
CAT_JOYSTICK = (0.30, 0.70, 0.60, 1)
CAT_MATH = (0.30, 0.65, 0.85, 1)
CAT_STRINGS = (0.55, 0.85, 0.75, 1)
CAT_PHYSICS = (0.45, 0.50, 0.85, 1)
CAT_PARTICLES = (0.95, 0.75, 0.40, 1)
CAT_AUDIO_ADV = (0.75, 0.55, 0.95, 1)
CAT_SCENES = (0.50, 0.65, 0.55, 1)
CAT_AI = (0.85, 0.45, 0.45, 1)
CAT_STORAGE = (0.65, 0.65, 0.75, 1)
CAT_NOTIFICATIONS = (0.95, 0.85, 0.40, 1)
CAT_ARVR = (0.45, 0.85, 0.85, 1)

# --- Espaçamento / geometria ------------------------------------------------
PADDING = 16
PADDING_SM = 8
PADDING_LG = 24
RADIUS = 14
RADIUS_SM = 8
TOUCH_MIN = 44                               # dp mínimo para alvos de toque

# --- Tipografia -------------------------------------------------------------
FONT_SIZE_TITLE = 22                          # "Kix" na app bar
FONT_SIZE_HEADING = 18                       # nome de projeto
FONT_SIZE_BODY = 14                          # labels de seção
FONT_SIZE_META = 12                          # datas e legendas


def hex_to_rgba(value: str) -> tuple[float, float, float, float]:
    """Converte '#RRGGBB' ou '#RRGGBBAA' para tupla RGBA no formato Kivy."""
    s = value.lstrip("#")
    if len(s) == 6:
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        return (r / 255, g / 255, b / 255, 1)
    if len(s) == 8:
        r, g, b, a = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), int(s[6:8], 16)
        return (r / 255, g / 255, b / 255, a / 255)
    raise ValueError(f"Cor inválida: {value!r}")