"""Renderiza mockups PNG das telas novas do Kix (M7).

Gera PNGs de cada tela nova (sem precisar de Kivy/GL):
- mock_01_dashboard.png
- mock_02_editor.png
- mock_03_object.png
- mock_04_categorias.png
- mock_05_categoria_evento.png (com hat-blocks)
- mock_06_formula_editor.png

Uso:
    python3 -m Kix.tools.render_mocks
    # gera em Kix/tools/mocks/*.png

Cada mock tem o mesmo tamanho (390x844 — iPhone 14) e usa as cores
do theme.py pra ficar visualmente próximo da implementação real.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# --- Cores (espelham Kix/core/theme.py) ------------------------------------
BG = (13, 13, 14)
SURFACE_1 = (18, 18, 20)
SURFACE_2 = (22, 22, 24)
SURFACE_3 = (28, 28, 31)
SURFACE_4 = (36, 36, 40)
TEXT_HIGH = (237, 237, 242)
TEXT_MED = (178, 178, 188)
TEXT_LOW = (115, 115, 128)
EMERALD = (16, 185, 129)
EMERALD_PRESSED = (13, 148, 104)
LAVANDA = (180, 168, 223)
LARANJA = (255, 152, 0)
WHITE = (255, 255, 255)

CAT_EVENT = (168, 71, 59)
CAT_CONTROL = (226, 160, 99)
CAT_MOTION = (60, 141, 207)
CAT_SOUND = (155, 89, 182)
CAT_LOOKS = (103, 173, 63)
CAT_PEN = (63, 127, 63)
CAT_DATA = (226, 104, 137)
CAT_DEVICE = (163, 143, 45)
CAT_FILES = (189, 183, 66)
CAT_USER = (60, 111, 229)
CAT_LIBS = (225, 143, 170)


# --- Fontes (tenta achar DejaVuSans; cai pra default) ----------------------
def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


# --- Helpers ---------------------------------------------------------------
def _rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = xy
    if fill is not None:
        draw.rounded_rectangle(xy, radius=radius, fill=fill, width=0)
    if outline is not None:
        draw.rounded_rectangle(xy, radius=radius, outline=outline, width=width)


def _text(draw, xy, text, fill=TEXT_HIGH, size=14, bold=False):
    f = _font(size, bold)
    draw.text(xy, text, font=f, fill=fill)


def _letter_avatar(draw, center, size, letter, color=SURFACE_3):
    """Quadrado cinza com letra centrada."""
    x, y = center
    box = (x - size // 2, y - size // 2, x + size // 2, y + size // 2)
    _rounded_rect(draw, box, radius=10, fill=color)
    f = _font(20, bold=True)
    bbox = draw.textbbox((0, 0), letter, font=f)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((x - w // 2, y - h // 2 - 2), letter, font=f, fill=TEXT_HIGH)


def _app_bar(draw, w, title, with_back=True, actions=("cast", "kebab")):
    """Top bar 56dp com título centralizado + ações à direita."""
    # bg
    draw.rectangle([0, 0, w, 56], fill=SURFACE_1)
    # back arrow
    if with_back:
        _text(draw, (16, 18), "←", fill=TEXT_HIGH, size=22)
    # título
    f = _font(16, bold=True)
    bbox = draw.textbbox((0, 0), title, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, 18), title, font=f, fill=TEXT_HIGH)
    # ações direita
    if actions:
        x = w - 16
        for a in reversed(actions):
            glyph = {"cast": "↗", "kebab": "⋮", "search": "🔍"}.get(a, a)
            bbox = draw.textbbox((0, 0), glyph, font=_font(18))
            aw = bbox[2] - bbox[0]
            draw.text((x - aw, 16), glyph, font=_font(18), fill=TEXT_HIGH)
            x -= aw + 28
    # linha sutil embaixo
    draw.line([0, 55, w, 55], fill=SURFACE_4, width=1)


def _fab(draw, w, bottom_y, glyph, color):
    """FAB circular 56dp com glifo."""
    x = w - 72
    draw.ellipse([x, bottom_y, x + 56, bottom_y + 56], fill=color)
    f = _font(26, bold=True)
    bbox = draw.textbbox((0, 0), glyph, font=f)
    gw = bbox[2] - bbox[0]
    gh = bbox[3] - bbox[1]
    draw.text((x + 28 - gw // 2, bottom_y + 28 - gh // 2 - 2),
              glyph, font=f, fill=WHITE)


# ============================================================================
# 1. DASHBOARD
# ============================================================================
def render_dashboard(out: Path) -> None:
    W, H = 390, 844
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    _app_bar(d, W, "KIX", with_back=False, actions=("kebab",))

    # área central: ícone pencil (FAB editar)
    cx, cy = W // 2, 230
    _rounded_rect(d, (cx - 28, cy - 28, cx + 28, cy + 28), radius=28, fill=SURFACE_2)
    _text(d, (cx - 6, cy - 14), "✎", fill=TEXT_MED, size=22)

    # FAB play verde (canto direito superior, acima do +)
    _fab(d, W, 640, "▶", EMERALD)

    # seção "PROJETOS"
    _text(d, (24, 696), "PROJETOS", fill=TEXT_MED, size=13, bold=True)
    # ícone de pasta à direita
    _text(d, (W - 50, 692), "📂", fill=TEXT_MED, size=18)

    # 4 cards
    cards = [
        ("P", "Projeto Principal", "Modificado há 2h", "14.2 MB"),
        ("J", "Jogo de Plataforma", "Modificado ontem", "8.7 MB"),
        ("M", "Mecânica de Física", "Modificado há 3 dias", "21.5 MB"),
        ("T", "Teste de IA", "Modificado há 1 semana", "2.1 MB"),
    ]
    for i, (letter, name, mod, size) in enumerate(cards):
        y = 730 + i * 78
        # card
        _rounded_rect(d, (16, y, W - 16, y + 70), radius=10, fill=SURFACE_3)
        # avatar
        _letter_avatar(d, (50, y + 35), 44, letter, color=SURFACE_4)
        # nome
        _text(d, (90, y + 14), name, fill=TEXT_HIGH, size=15, bold=True)
        # modificado
        _text(d, (90, y + 36), f"{mod}  •  {size}", fill=TEXT_LOW, size=11)
        # kebab
        _text(d, (W - 36, y + 26), "⋮", fill=TEXT_MED, size=18)

    # FAB +
    _fab(d, W, 32, "+", EMERALD)

    img.save(out)


# ============================================================================
# 2. EDITOR (Pocket Code style: Fundo + Atores e objetos, sem tab bar)
# ============================================================================
def render_editor(out: Path) -> None:
    W, H = 390, 844
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    _app_bar(d, W, "Among Us ReWorked", with_back=True, actions=("cast", "kebab"))

    # Fundo row
    y = 80
    _rounded_rect(d, (16, y, W - 16, y + 72), radius=10, fill=SURFACE_3)
    # thumb quadrado cinza
    _rounded_rect(d, (28, y + 8, 84, y + 64), radius=8, fill=SURFACE_4)
    _text(d, (40, y + 22), "Fundo", fill=TEXT_HIGH, size=15, bold=True)

    # section header
    y = 180
    _text(d, (16, y), "Atores e objetos", fill=TEXT_MED, size=14)

    # objeto row "Team"
    y = 216
    _rounded_rect(d, (16, y, W - 16, y + 64), radius=10, fill=SURFACE_2)
    # play triangle lavanda
    cx, cy = 50, y + 32
    draw = d
    # triângulo ▶ em círculo lavanda
    draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=LAVANDA)
    draw.polygon([(cx - 6, cy - 10), (cx - 6, cy + 10), (cx + 10, cy)],
                 fill=WHITE)
    # nome
    _text(d, (90, y + 22), "Team", fill=TEXT_HIGH, size=15, bold=True)
    # kebab
    _text(d, (W - 36, y + 22), "⋮", fill=TEXT_MED, size=18)

    # segundo objeto (placeholder)
    y = 296
    _rounded_rect(d, (16, y, W - 16, y + 64), radius=10, fill=SURFACE_2)
    draw.ellipse([28, cy - 22 + 80, 72, cy + 22 + 80], fill=LAVANDA)
    draw.polygon([(50 - 6, cy - 10 + 80), (50 - 6, cy + 10 + 80),
                  (50 + 10, cy + 80)], fill=WHITE)
    _text(d, (90, y + 22), "Impostor", fill=TEXT_HIGH, size=15, bold=True)
    _text(d, (W - 36, y + 22), "⋮", fill=TEXT_MED, size=18)

    # FAB play lavanda
    _fab(d, W, 104, "▶", LAVANDA)
    # FAB + lavanda
    _fab(d, W, 32, "+", LAVANDA)

    img.save(out)


# ============================================================================
# 3. OBJECT SCREEN (Scripts/Looks/Sounds tabs)
# ============================================================================
def render_object_screen(out: Path) -> None:
    W, H = 390, 844
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    _app_bar(d, W, "Meu ator ou objeto", with_back=True, actions=("kebab",))

    # tabs Scripts | Looks | Sounds
    tabs = [
        ("📋", "Scripts", True),
        ("👁", "Looks", False),
        ("🔊", "Sounds", False),
    ]
    tab_w = W // 3
    for i, (icon, label, sel) in enumerate(tabs):
        x0 = i * tab_w + 8
        x1 = (i + 1) * tab_w - 8
        y0 = 72
        y1 = 128
        fill = SURFACE_3 if sel else SURFACE_2
        _rounded_rect(d, (x0, y0, x1, y1), radius=8, fill=fill)
        # ícone + label
        f = _font(18, bold=False)
        bbox = d.textbbox((0, 0), icon, font=f)
        iw = bbox[2] - bbox[0]
        d.text(((x0 + x1) // 2 - iw // 2, y0 + 10), icon, font=f,
               fill=TEXT_HIGH if sel else TEXT_MED)
        f2 = _font(11, bold=True)
        bbox = d.textbbox((0, 0), label, font=f2)
        lw = bbox[2] - bbox[0]
        d.text(((x0 + x1) // 2 - lw // 2, y0 + 42), label, font=f2,
               fill=TEXT_HIGH if sel else TEXT_MED)

    # mensagem central
    _text(d, (W // 2 - 130, 480), 'Toque em "+" para adicionar Scripts',
          fill=TEXT_MED, size=15, bold=False)

    # FAB play (verde no ObjectScreen, segundo a screenshot)
    _fab(d, W, 104, "▶", LAVANDA)
    _fab(d, W, 32, "+", LAVANDA)

    img.save(out)


# ============================================================================
# 4. CATEGORIAS — 11 linhas coloridas full-width
# ============================================================================
def render_categorias(out: Path) -> None:
    W, H = 390, 844
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    _app_bar(d, W, "Categorias", with_back=True, actions=("search", "kebab"))

    cats = [
        ("Evento", CAT_EVENT),
        ("Controle", CAT_CONTROL),
        ("Movimento", CAT_MOTION),
        ("Som", CAT_SOUND),
        ("Aparências", CAT_LOOKS),
        ("Caneta", CAT_PEN),
        ("Dados", CAT_DATA),
        ("Dispositivo", CAT_DEVICE),
        ("Arquivos", CAT_FILES),
        ("Seus blocos", CAT_USER),
        ("Bibliotecas", CAT_LIBS),
    ]
    y = 56
    for i, (label, color) in enumerate(cats):
        # faixa colorida (separadas por linha fina)
        draw_rect_y = y + i * 72
        d.rectangle([0, draw_rect_y, W, draw_rect_y + 72], fill=color)
        # label branco bold esquerda-aligned
        _text(d, (24, draw_rect_y + 22), label, fill=WHITE, size=18, bold=True)

    # FABs laranja (estilo Pocket Code Categorias)
    _fab(d, W, 104, "▶", LARANJA)
    _fab(d, W, 32, "+", LARANJA)

    img.save(out)


# ============================================================================
# 5. CATEGORIA EVENTO — lista de hat-blocks (topo convexo)
# ============================================================================
def _draw_hat_block(d, x, y, w, h, color):
    """Desenha bloco formato hat: topo curvo convexo + corpo retangular."""
    # corpo
    d.rounded_rectangle([x, y + 12, x + w, y + h], radius=8, fill=color)
    # arco convexo no topo (semicírculo)
    cx = x + w // 2
    cy = y + 12
    r = w // 2
    pts = []
    steps = 24
    for i in range(steps + 1):
        t = math.pi * i / steps
        px = cx - r * math.cos(t)
        py = cy + (r * 0.18) * math.sin(t)
        pts.append((px, py))
    d.line(pts, fill=color, width=18)


def _draw_regular_block(d, x, y, w, h, color):
    d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=color)


def render_categoria_evento(out: Path) -> None:
    W, H = 390, 844
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    _app_bar(d, W, "Evento", with_back=True, actions=())

    # hat-blocks
    hats = [
        "Quando a cena começar",
        "Quando tocado",
        "Quando a tela for pressionada",
        "Quando o sprite for solto",
        "Quando o dedo mover sobre o sprite",
        "Quando o dedo mover na tela",
        "Quando você receber mensagem 1",
    ]
    y = 72
    for label in hats:
        _draw_hat_block(d, 12, y, W - 24, 44, CAT_EVENT)
        _text(d, (28, y + 18), label, fill=WHITE, size=14, bold=False)
        y += 50

    # blocos não-hat (laranja claro)
    non_hats = [
        ("Enviar mensagem 1", True),     # mais claro
        ("Enviar e aguardar mensagem 1", True),
        ("Quando o sinal for recebido 'mensagem 1' salvar parâmetros em novo...", False),
        ("Transmitir a todos com parâmetros Sinal 'mensagem 1' Parâmetros 'any data...'", False),
    ]
    for label, light in non_hats:
        col = (CAT_CONTROL if light else CAT_EVENT)
        _draw_regular_block(d, 12, y, W - 24, 44, col)
        _text(d, (28, y + 14), label, fill=WHITE, size=13, bold=False)
        y += 50

    # FABs laranja
    _fab(d, W, 104, "▶", LARANJA)
    _fab(d, W, 32, "+", LARANJA)

    img.save(out)


# ============================================================================
# 6. FORMULA EDITOR
# ============================================================================
def render_formula_editor(out: Path) -> None:
    W, H = 390, 844
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    _app_bar(d, W, "Editor de fórmula", with_back=True,
             actions=("undo", "files", "redo"))

    # bloco "Definir variável X para Y"
    y = 72
    _rounded_rect(d, (12, y, W - 12, y + 44), radius=8, fill=SURFACE_3)
    _text(d, (24, y + 14), "Definir variável", fill=TEXT_HIGH, size=14)
    _rounded_rect(d, (148, y + 8, 220, y + 36), radius=4, fill=SURFACE_4)
    _text(d, (155, y + 14), "X", fill=TEXT_HIGH, size=14, bold=True)
    _text(d, (232, y + 14), "para", fill=TEXT_HIGH, size=14)
    _rounded_rect(d, (266, y + 8, 340, y + 36), radius=4, fill=SURFACE_4)
    _text(d, (273, y + 14), "Y", fill=TEXT_HIGH, size=14, bold=True)

    # display da expressão (texto branco)
    y += 56
    _rounded_rect(d, (12, y, W - 12, y + 56), radius=8, fill=SURFACE_2)
    _text(d, (24, y + 18), "1 + 2 × 3", fill=TEXT_HIGH, size=22, bold=True)

    # chips: Funções / Propriedades / [📋] / [📁]
    y += 72
    chips = [("Funções", SURFACE_3), ("Propriedades", SURFACE_3),
             ("📋", SURFACE_3), ("📁", SURFACE_3)]
    cx = 16
    for label, color in chips:
        w = 80 if len(label) > 4 else 40
        _rounded_rect(d, (cx, y, cx + w, y + 32), radius=8, fill=color)
        _text(d, (cx + 10, y + 8), label, fill=TEXT_HIGH, size=12)
        cx += w + 8

    # linha 2 chips: Sensores / Lógica / Dado
    y += 40
    for label in ("Sensores", "Lógica", "Dado"):
        _rounded_rect(d, (cx - 8 - 70, y, cx - 8, y + 32), radius=8, fill=SURFACE_3)
        _text(d, (cx - 8 - 60, y + 8), label, fill=TEXT_HIGH, size=12)
        cx -= 78

    # teclado numérico
    y += 60
    keys = [
        ["7", "8", "9", "⌫"],
        ["4", "5", "6", "÷"],
        ["1", "2", "3", "×"],
        ["(", ")", "0", "."],
    ]
    ops = {"÷": True, "×": True, "⌫": True}
    for row in keys:
        cx = 16
        for k in row:
            color = SURFACE_3 if k in "0123456789.()" else SURFACE_2
            _rounded_rect(d, (cx, y, cx + 70, y + 56), radius=8, fill=color)
            _text(d, (cx + 28, y + 16), k, fill=TEXT_HIGH, size=20, bold=True)
            cx += 80
        y += 64

    # Abc (lateral esquerdo)
    _rounded_rect(d, (16, y, 60, y + 56), radius=8, fill=LARANJA)
    _text(d, (24, y + 18), "Abc", fill=WHITE, size=14, bold=True)
    # Calcular (verde direita)
    _rounded_rect(d, (76, y, W - 16, y + 56), radius=8, fill=EMERALD)
    f = _font(18, bold=True)
    bbox = d.textbbox((0, 0), "Calcular", font=f)
    cw = bbox[2] - bbox[0]
    d.text((76 + ((W - 16) - 76) // 2 - cw // 2, y + 18),
           "Calcular", font=f, fill=WHITE)

    img.save(out)


# ============================================================================
# main
# ============================================================================
def main() -> None:
    out_dir = Path(__file__).parent / "mocks"
    out_dir.mkdir(parents=True, exist_ok=True)

    render_dashboard(out_dir / "mock_01_dashboard.png")
    render_editor(out_dir / "mock_02_editor.png")
    render_object_screen(out_dir / "mock_03_object.png")
    render_categorias(out_dir / "mock_04_categorias.png")
    render_categoria_evento(out_dir / "mock_05_categoria_evento.png")
    render_formula_editor(out_dir / "mock_06_formula_editor.png")

    print(f"Mockups gerados em {out_dir}:")
    for p in sorted(out_dir.glob("*.png")):
        size = p.stat().st_size
        print(f"  {p.name:35} {size // 1024} KB")


if __name__ == "__main__":
    main()
