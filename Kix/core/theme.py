"""Design tokens do Kix — M7.

Tema unificado conforme Prompt Milimétrico (seções 1, 1.1, 2, 2.1, 2.2, 3.1):

- Fundo preto (#000000) como ``--bg-base`` único da app.
- Emerald (#10B981) reservado para UI de marca (FAB, foco, ação primária).
- 9 cores canônicas do Pocket Code para categorias funcionais — Tom principal
  exato; Tom secundário derivado via ``lighten(+0.18)`` para blocos de ação.
- 8 cores extras do Kix (Fase 1B — spec seção 3.1): physics, network, storage,
  particles, ai, tilemap, economy, python (esta última categoria especial
  per spec seção 3.3 — extensibilidade total via Python/Kivy).
- Tokens geométricos da silhueta "bandeirola" dos blocos (spec 2.2):
  amplitude de onda, raio de canto, alturas, posições de ícone e texto.

Valores em RGBA (0.0–1.0) — formato aceito pelo Kivy.
Comentário ao lado de cada constante registra o token CSS equivalente da spec.
"""

from __future__ import annotations

# --- 1. Base (--bg-base, --surface-*, --border-subtle, --text-*) ---------

BG          = (0.000, 0.000, 0.000, 1)   # --bg-base        #000000
SURFACE_1   = (0.102, 0.102, 0.102, 1)   # --surface-1      #1A1A1A
SURFACE_2   = (0.078, 0.078, 0.078, 1)   # --surface-2      #141414
SURFACE_3   = (0.051, 0.051, 0.051, 1)   # --surface-3      #0D0D0D
SURFACE_4   = (0.141, 0.141, 0.141, 1)   # --border-subtle  #242424

WHITE       = (1.000, 1.000, 1.000, 1)   # --text-primary   #FFFFFF
TEXT_HIGH   = (1.000, 1.000, 1.000, 1)   # --text-primary   (alias semântico)
TEXT_MED    = (0.620, 0.620, 0.620, 1)   # --text-secondary #9E9E9E
TEXT_LOW    = (0.361, 0.361, 0.361, 1)   # --text-muted     #5C5C5C

# --- 1.1 Emerald (cor de marca única) ------------------------------------

EMERALD         = (0.063, 0.725, 0.506, 1)   # --emerald-500  #10B981
EMERALD_PRESSED = (0.051, 0.620, 0.443, 1)   # --emerald-600  #0D9E71
EMERALD_300     = (0.431, 0.906, 0.718, 1)   # --emerald-300  #6EE7B7
EMERALD_900     = (0.024, 0.169, 0.122, 1)   # --emerald-900  #062B1F
ON_EMERALD      = (0.016, 0.078, 0.051, 1)   # --on-emerald   #04140D
DANGER          = (0.937, 0.267, 0.267, 1)   # --danger       #EF4444

# --- 2. 9 cores Pocket Code (Tom principal) -----------------------------

# Catálogo oficial Pocket Code: ver spec seção 2. Cada categoria tem Tom
# principal (header / blocos estruturais) e Tom secundário (blocos de ação).
# Tom secundário NÃO é derivado de fórmula — é o valor exato da spec
# (lighten ≈+18% em RGB produz desvios visíveis).

CAT_EVENT   = (0.941, 0.463, 0.169, 1)   # Evento      Tom principal #F0762B
CAT_CONTROL = (0.957, 0.635, 0.369, 1)   # Controle    Tom principal #F4A25E
CAT_MOTION  = (0.247, 0.569, 0.827, 1)   # Movimento   Tom principal #3F91D3
CAT_SOUND   = (0.608, 0.373, 0.820, 1)   # Som         Tom principal #9B5FD1
CAT_LOOKS   = (0.447, 0.690, 0.263, 1)   # Aparências  Tom principal #72B043
CAT_PEN     = (0.243, 0.420, 0.122, 1)   # Caneta      Tom principal #3E6B1F
CAT_DATA    = (0.941, 0.392, 0.353, 1)   # Dados       Tom principal #F0645A
CAT_DEVICE  = (0.627, 0.541, 0.122, 1)   # Dispositivo Tom principal #A08A1F
CAT_FILES   = (0.710, 0.761, 0.165, 1)   # Arquivos    Tom principal #B5C22A

CAT_EVENT_LIGHT   = (0.957, 0.572, 0.302, 1)   # #F4924D
CAT_CONTROL_LIGHT = (0.969, 0.737, 0.522, 1)   # #F7BC85
CAT_MOTION_LIGHT  = (0.420, 0.682, 0.878, 1)   # #6BAEE0
CAT_SOUND_LIGHT   = (0.710, 0.533, 0.890, 1)   # #B588E3
CAT_LOOKS_LIGHT   = (0.576, 0.784, 0.416, 1)   # #93C86A
CAT_PEN_LIGHT     = (0.369, 0.561, 0.239, 1)   # #5E8F3D
CAT_DATA_LIGHT    = (0.957, 0.561, 0.529, 1)   # #F48F87
CAT_DEVICE_LIGHT  = (0.749, 0.647, 0.239, 1)   # #BFA53D
CAT_FILES_LIGHT   = (0.796, 0.839, 0.369, 1)   # #CBD65E

# --- Categorias extras do Kix (spec seção 3.1) ----------------------------
# Paleta curada conforme tabela Seção 3.1 do Prompt Milimétrico. Cada
# categoria tem Tom principal exato da spec + Tom secundário derivado.
# CAT_STORAGE usa luminosidade/saturação baixas deliberadamente (spec):
# "propositalmente baixas para não competir com --emerald-500 de marca".

CAT_PHYSICS   = (0.761, 0.255, 0.047, 1)   # Física/Colisão  #C2410C (terracota)
CAT_PHYSICS_LIGHT   = (0.878, 0.541, 0.361, 1)   # #E08A5C

CAT_NETWORK   = (0.184, 0.663, 0.631, 1)   # Rede/Multiplayer #2FA9A1 (teal petróleo)
CAT_NETWORK_LIGHT   = (0.435, 0.788, 0.761, 1)   # #6FC9C2

CAT_STORAGE   = (0.024, 0.373, 0.275, 1)   # Banco/Persistência #065F46 (verde escuro, low-contrast)
CAT_STORAGE_LIGHT   = (0.239, 0.612, 0.486, 1)   # #3D9C7C

CAT_ECONOMY   = (0.792, 0.541, 0.016, 1)   # Economia #CA8A04 (dourado envelhecido)
CAT_ECONOMY_LIGHT   = (0.910, 0.757, 0.361, 1)   # #E8C15C

CAT_PARTICLES = (0.486, 0.227, 0.929, 1)   # Partículas/Efeitos #7C3AED (violeta profundo)
CAT_PARTICLES_LIGHT = (0.655, 0.545, 0.980, 1)   # #A78BFA

CAT_AI        = (0.357, 0.431, 0.961, 1)   # IA/Comportamento  #5B6EF5 (índigo)
CAT_AI_LIGHT        = (0.549, 0.596, 0.973, 1)   # #8C98F8

CAT_TILEMAP   = (0.471, 0.443, 0.424, 1)   # Tiles #78716C (stone/cinza-amarronzado)
CAT_TILEMAP_LIGHT   = (0.659, 0.635, 0.620, 1)   # #A8A29E

CAT_PYTHON    = (0.216, 0.463, 0.671, 1)   # Python Puro #3776AB (azul Python oficial) — categoria especial (spec 3.3)
CAT_PYTHON_LIGHT    = (0.435, 0.659, 0.847, 1)   # #6FA8D8

# Texto customizável (M8) — slate-500 neutro, distinto de EXTRAS
# (#64748B, mais saturado) e TILEMAP (#78716C, warm). Família cinza,
# temperatura neutra para "formatação de texto".
CAT_TEXT      = (0.420, 0.447, 0.502, 1)   # Texto #6B7280 (slate-500 neutro)
CAT_TEXT_LIGHT      = (0.612, 0.639, 0.686, 1)   # #9CA3AF

CAT_EXTRAS    = (0.392, 0.455, 0.545, 1)   # Blocos Extras #64748B (cinza-azulado neutro, spec 3.2/5)
CAT_EXTRAS_LIGHT    = (0.612, 0.663, 0.729, 1)   # #9CA9BA

# --- Aliases para sub-categorias que consolidam em "Blocos Extras" ------
# Spec seção 5 regra 6: "Funcionalidades situacionais/de hardware não
# viram categoria própria — todas vivem juntas em Blocos Extras".
# Mantemos os nomes CAT_CAMERA etc. como aliases retro-compatíveis para
# não quebrar imports em Kix/blocks/*.py.

CAT_CAMERA       = CAT_EXTRAS   # câmera/AR → Blocos Extras
CAT_JOYSTICK     = CAT_EXTRAS   # joystick (hardware) → Blocos Extras
CAT_ARVR         = CAT_EXTRAS   # AR/VR → Blocos Extras
CAT_NOTIFICATIONS = CAT_EXTRAS  # notificações → Blocos Extras

# --- Demais categorias Kix (não constam da spec 3.1; valores mantidos) --
# Estas continuam com tons placeholder — aguardando spec para cor canônica.

CAT_USER          = (0.30, 0.35, 0.75, 1)
CAT_LIBS          = (0.95, 0.55, 0.85, 1)
CAT_LAYERS        = (0.55, 0.55, 0.65, 1)
CAT_SHADERS       = (0.75, 0.50, 0.85, 1)
CAT_UI            = (0.20, 0.55, 0.55, 1)
CAT_SPRITESHEET   = (0.85, 0.55, 0.35, 1)
CAT_MATH          = (0.30, 0.65, 0.85, 1)
CAT_STRINGS       = (0.55, 0.85, 0.75, 1)
CAT_AUDIO_ADV     = (0.75, 0.55, 0.95, 1)
CAT_SCENES        = (0.50, 0.65, 0.55, 1)

# --- Aliases semânticos (Fase 1A) ----------------------------------------
# Mapeiam uso → cor. Sobrevivem ao renomeio de SURFACE_* porque o nome da
# constante descreve a *função*, não o tom. Usar estes nomes ao invés de
# SURFACE_X direto sempre que a intenção for semântica.

CARD_BG             = SURFACE_1   # ProjectCard, cards de listagem
INPUT_BG            = SURFACE_1   # TextInput
BUTTON_BG_SECONDARY = SURFACE_1   # KixButton quando não primário
PRESSED_BG          = SURFACE_4   # estado :down de botão secundário
HEADER_BG           = SURFACE_2   # app bar / header
MODAL_BG            = SURFACE_2   # popup / menu contextual
MODAL_OVERLAY       = (0, 0, 0, 0.7)   # scrim atrás de modal (spec 4)
ACCORDION_BG        = SURFACE_3   # fundo de seção agrupada

# --- Espaçamento / geometria ---------------------------------------------

PADDING     = 16
PADDING_SM  = 8
PADDING_LG  = 24
RADIUS      = 14
RADIUS_SM   = 8
TOUCH_MIN   = 44

# --- Tipografia ---------------------------------------------------------

FONT_SIZE_TITLE   = 22   # "Kix" na app bar
FONT_SIZE_HEADING = 18   # nome de projeto
FONT_SIZE_BODY    = 14   # labels de seção
FONT_SIZE_META    = 12   # datas e legendas


# --- Helpers ------------------------------------------------------------

# Mapeamento categoria Pocket Code + extras spec 3.1 → (base, light).
# Categorias fora desta tabela (math, strings, user, libs, etc.) não têm
# two-tone canônico — use a constante CAT_X diretamente.
_CAT_TABLE: dict[str, tuple[tuple[float, float, float, float], tuple[float, float, float, float]]] = {
    # Pocket Code canônico (spec 2)
    "event":   (CAT_EVENT,   CAT_EVENT_LIGHT),
    "control": (CAT_CONTROL, CAT_CONTROL_LIGHT),
    "motion":  (CAT_MOTION,  CAT_MOTION_LIGHT),
    "sound":   (CAT_SOUND,   CAT_SOUND_LIGHT),
    "looks":   (CAT_LOOKS,   CAT_LOOKS_LIGHT),
    "pen":     (CAT_PEN,     CAT_PEN_LIGHT),
    "data":    (CAT_DATA,    CAT_DATA_LIGHT),
    "device":  (CAT_DEVICE,  CAT_DEVICE_LIGHT),
    "files":   (CAT_FILES,   CAT_FILES_LIGHT),
    # Extras Kix com paleta curada (spec 3.1)
    "physics":   (CAT_PHYSICS,   CAT_PHYSICS_LIGHT),
    "network":   (CAT_NETWORK,   CAT_NETWORK_LIGHT),
    "storage":   (CAT_STORAGE,   CAT_STORAGE_LIGHT),
    "economy":   (CAT_ECONOMY,   CAT_ECONOMY_LIGHT),
    "particles": (CAT_PARTICLES, CAT_PARTICLES_LIGHT),
    "ai":        (CAT_AI,        CAT_AI_LIGHT),
    "tilemap":   (CAT_TILEMAP,   CAT_TILEMAP_LIGHT),
    "python":    (CAT_PYTHON,    CAT_PYTHON_LIGHT),
    # "Blocos Extras" — categoria unificada para hardware/situacional
    # (GPS, câmera/AR, IoT, acessibilidade, social share, vibração, lanterna).
    # Spec 3.2 + regra 6 da Seção 5: "Funcionalidades situacionais/de
    # hardware não viram categoria própria — todas vivem juntas em Blocos
    # Extras (#64748B)".
    "extras":    (CAT_EXTRAS,    CAT_EXTRAS_LIGHT),
}


def cat_color(name: str, tone: str = "base") -> tuple[float, float, float, float]:
    """Tom principal (``'base'``) ou Tom secundário (``'light'``) de categoria.

    ``name`` é o nome curto da categoria Pocket Code ou Kix sem prefixo
    ``CAT_`` (ex: ``'event'``, ``'physics'``, ``'python'``).

    ``tone='light'`` devolve o Tom secundário exato da spec — réplique da
    regra Pocket Code em que blocos de "ação/comando" dentro de uma categoria
    ficam visualmente mais claros que os blocos estruturais (header/gatilho).

    Categoria desconhecida → ``SURFACE_3`` (fallback neutro).
    """
    pair = _CAT_TABLE.get(name)
    if pair is None:
        return SURFACE_3
    if tone == "base":
        return pair[0]
    if tone == "light":
        return pair[1]
    raise ValueError(f"tone deve ser 'base' ou 'light', recebeu {tone!r}")


# --- 2.2 Geometria do bloco (bandeirola / ribbon) ------------------
# Silhueta: bordas superior/inferior como 1 curva Bézier quadrática cada
# (amplitude BLOCK_WAVE_AMPLITUDE). Vértices onda↔lateral arredondados em
# BLOCK_CORNER_RADIUS. Empilhados sem gap (BLOCK_GAP_STACKED = 0) — a onda
# inferior do bloco N encaixa na onda superior do bloco N+1.

BLOCK_WAVE_AMPLITUDE  = 8        # --block-wave-amplitude    altura da "barriga"
BLOCK_CORNER_RADIUS   = 4        # --block-corner-radius     suavização vértice
BLOCK_MIN_HEIGHT      = 90       # --block-min-height        bloco 1 linha
BLOCK_HEIGHT_2_LINES  = 140      # --block-height-2-lines    bloco 2 linhas
BLOCK_PADDING_LEFT    = 24       # --block-padding-left      ícone → borda esquerda
BLOCK_ICON_SIZE       = 32       # --block-icon-size         ícone quadrado 32×32
BLOCK_TEXT_START_X    = 88       # --block-text-start-x      texto após ícone + respiro
BLOCK_GAP_STACKED     = 0        # --block-gap-stacked       blocos da mesma pilha colados
BLOCK_PARAM_UNDERLINE = (1, 1, 1, 0.6)   # rgba(255,255,255,0.6) — sublinhado 1.5px
BLOCK_ICON_OUTLINE    = (1, 1, 1, 0.85)  # rgba(255,255,255,0.85) — contorno único
BLOCK_SHADOW_DRAG_A   = 0.45     # --block-shadow-dragging  rgba(0,0,0,0.45)
BLOCK_FONT_SIZE_SP    = "18sp"   # --block-text-size  (spec: 18-19sp; valor central)

# --- 3.3 Code editor (bloco Python Puro) ----------------------------------
# Coluna fixa de numeração de linha, fonte monoespaçada 14sp, altura
# mínima 3 linhas (spec: "altura mínima 3 linhas, expansível conforme
# conteúdo (auto-grow), até CODE_MAX_LINES antes de scrollar).
CODE_GUTTER_W   = 24         # --code-gutter-width       coluna numeração
CODE_FONT_SIZE  = "14sp"     # --code-font-size          fonte monoespaçada
CODE_MIN_LINES  = 3          # --code-min-lines          altura inicial
CODE_MAX_LINES  = 12         # --code-max-lines          antes do scroll


def hex_to_rgba(value: str) -> tuple[float, float, float, float]:
    """Converte '#RRGGBB' ou '#RRGGBBAA' para tupla RGBA no formato Kivy.

    Mantido para compatibilidade com importadores externos.
    """
    s = value.lstrip("#")
    if len(s) == 6:
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        return (r / 255, g / 255, b / 255, 1)
    if len(s) == 8:
        r, g, b, a = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), int(s[6:8], 16)
        return (r / 255, g / 255, b / 255, a / 255)
    raise ValueError(f"Cor inválida: {value!r}")