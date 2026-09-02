"""Renderer da silhueta 'bandeirola/ribbon' dos blocos Kix (spec 2.2).

Geometria:
- Top edge: 1 curva Bézier quadrática de (left, top) → (right, top) com apex
  em y = top - amplitude. (Spec 2.2: "uma única curva Bézier quadrática por
  borda, não múltiplas ondas".)
- Bottom edge: espelhada, apex em y = bottom + amplitude.
- Sides: retas, vértices onda↔lateral com inset de BLOCK_CORNER_RADIUS para
  suavizar a junção (spec 2.2, "raio 3-4px").
- Empilhamento: bloco N e N+1 encostam (gap 0); a onda inferior de N alinha
  com a onda superior de N+1, dando continuidade visual.

Preenchimento: triangulado via ``Mesh`` (Kivy não tem ``Polygon`` nativo;
``Line`` só desenha contorno, sem fill).

Todas as coordenadas de entrada estão em PIXELS — a conversão ``dp()`` é
responsabilidade do caller (mesmo padrão do resto do Kix).
"""

from __future__ import annotations

from typing import Tuple

from kivy.graphics import Color, Line, Mesh

from Kix.core.theme import BLOCK_CORNER_RADIUS, BLOCK_ICON_OUTLINE, BLOCK_PARAM_UNDERLINE


def bandeirola_mesh(
    width: float,
    height: float,
    amplitude: float,
    corner_radius: float = BLOCK_CORNER_RADIUS,
    segments: int = 12,
) -> Tuple[list[float], list[int]]:
    """Triangula a bandeirola como ``(vertices, indices)`` para ``Mesh``.

    Polígono (sentido anti-horário a partir do canto sup-esq):
      - Top wave (n+1 pts):  de (r, 0) → (W-r, 0), apex em (W/2, -amp)
      - Right side:          (W, r) → (W, H-r)
      - Bottom wave (n+1):   (W-r, H) → (r, H), apex em (W/2, H+amp)
      - Left side:           (0, H-r) → (0, r)

    Onde ``r`` = corner_radius clamped a ``min(W, H) / 4``.

    Bézier quadrática aproximada: y_i = ±4·amp·t·(1-t). É a forma paramétrica
    exata para uma Bézier quadrática com pontos de controle em
    (mid_x, ±2·amp) — apex em y=±amp no t=0.5 (correto).
    """
    r = min(corner_radius, width / 2, height / 2)

    top_pts = []
    for i in range(segments + 1):
        t = i / segments
        x = r + (width - 2 * r) * t
        y = -4 * amplitude * t * (1 - t)
        top_pts.append((x, y))

    bot_pts = []
    for i in range(segments + 1):
        t = i / segments
        x = r + (width - 2 * r) * t
        y = height + 4 * amplitude * t * (1 - t)
        bot_pts.append((x, y))

    vertices = []
    for p in top_pts:
        vertices.extend([p[0], p[1], 0])
    for p in bot_pts:
        vertices.extend([p[0], p[1], 0])

    indices = []
    for i in range(segments):
        t_i = i
        t_next = i + 1
        b_i = (segments + 1) + i
        b_next = (segments + 1) + i + 1
        indices.extend([t_i, t_next, b_next])  # triângulo sup
        indices.extend([t_i, b_next, b_i])     # triângulo inf

    return vertices, indices


# --- Bandeirola como background de widget ------------------------------


def draw_bandeirola_bg(widget, color, amplitude: float) -> Tuple[Color, Mesh]:
    """Desenha a bandeirola em ``widget.canvas.before`` e devolve ``(Color, Mesh)``.

    O caller deve chamar ``reposition_bandeirola(mesh, widget, amplitude)``
    quando o tamanho do widget mudar (mesmo padrão de cards/botões).
    """
    verts, idx = bandeirola_mesh(widget.width, widget.height, amplitude)
    with widget.canvas.before:
        bg = Color(*color)
        mesh = Mesh(vertices=verts, indices=idx, mode="triangles")
    return bg, mesh


def reposition_bandeirola(mesh: Mesh, widget, amplitude: float) -> None:
    """Recalcula vértices quando o widget muda de tamanho.

    Mais barato que redesenhar — só substitui os arrays do Mesh.
    """
    verts, idx = bandeirola_mesh(widget.width, widget.height, amplitude)
    mesh.vertices = verts
    mesh.indices = idx


def set_bandeirola_color(bg: Color, color) -> None:
    """Troca a cor de fundo (ex: estado :down → cor pressionada)."""
    bg.rgba = color


# --- Ícone do bloco (32×32, dobra triangular + linhas de roteiro) -----


def draw_block_icon(
    widget, x: float, y: float, size: float = 32, canvas=None
) -> None:
    """Desenha o ícone 'página com dobra' no canto esquerdo do bloco.

    - Quadrado ``size`` × ``size`` com canto sup-esq dobrado (triângulo).
    - 3 linhas horizontais finas dentro, representando 'script'.
    - Contorno único ``BLOCK_ICON_OUTLINE`` para TODAS as categorias
      (spec 2.2: "O mesmo ícone é usado em todas as categorias. Ele não
      muda de forma; somente a cor do contorno acompanha
      rgba(255,255,255,0.85)").

    Coordenadas: ``(x, y)`` = canto inferior-esquerdo do ícone (convenção
    Kivy: y cresce para cima).

    ``canvas`` opcional: canvas alvo (default ``widget.canvas``). Use
    ``widget.canvas.before`` para desenhar abaixo dos filhos (entre fill
    e children), ou ``widget.canvas.after`` para ficar acima dos filhos.
    """
    fold = size * 0.25  # dobra = 25% do lado (~8px em ícone 32px)
    ctx = canvas if canvas is not None else widget.canvas

    with ctx:
        Color(*BLOCK_ICON_OUTLINE)

        # 1) Contorno da "página" (caminho fechado):
        #    canto-com-dobra (fold, 0) → topo dir (s, 0) → inf dir (s, s)
        #    → inf esq (0, s) → sobe até dobra (0, fold) → diagonal volta.
        page_pts = [
            x + fold, y,
            x + size, y,
            x + size, y + size,
            x, y + size,
            x, y + fold,
            x + fold, y,
        ]
        Line(points=page_pts, width=1.2, close=True)

        # 2) "Dobra" propriamente dita — triângulo no canto:
        #    (0, fold) → (fold, fold) → (fold, 0).
        Line(points=[x, y + fold, x + fold, y + fold, x + fold, y], width=1.0)

        # 3) Linhas de "roteiro" — 3 linhas horizontais finas internas.
        m = size * 0.18
        top_pad = size * 0.42
        line_gap = size * 0.16
        for i in range(3):
            line_y = y + top_pad + i * line_gap
            Line(points=[x + m, line_y, x + size - m, line_y], width=0.8)


# --- Sublinhado de parâmetro (1.5px, rgba(255,255,255,0.6)) -----------


def draw_param_underline(widget, x: float, y: float, width: float) -> None:
    """Sublinhado 1.5px sob um valor editável (spec 2.2).

    Cor: ``BLOCK_PARAM_UNDERLINE``. Use abaixo do label do parâmetro.
    """
    with widget.canvas:
        Color(*BLOCK_PARAM_UNDERLINE)
        Line(points=[x, y, x + width, y], width=1.5)


# --- Ícone "cobra Python" para categoria python (spec seção 3.3) -------


def _cubic_bezier_points(p0, p1, p2, p3, n: int = 28) -> list[float]:
    """Amostra cubic Bezier em n+1 pontos; devolve flat list[float]."""
    pts: list[float] = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = (u**3 * p0[0] + 3 * u**2 * t * p1[0]
             + 3 * u * t**2 * p2[0] + t**3 * p3[0])
        y = (u**3 * p0[1] + 3 * u**2 * t * p1[1]
             + 3 * u * t**2 * p2[1] + t**3 * p3[1])
        pts.extend([x, y])
    return pts


def draw_python_cobra_icon(
    widget,
    x: float,
    y: float,
    size: float = 32,
    canvas=None,
    color=None,
) -> None:
    """Logotipo simplificado da cobra do Python (spec seção 3.3).

    Dois arcos cúbicos entrelaçados formando um padrão simétrico de "8
    rotacionado" — convenção visual da cobra do Python, simplificada
    para encaixar no slot 32×32 do bloco. Cada arco termina em uma
    cabeça (ponto pequeno) reforçando a leitura de "duas cobras".

    Coordenadas: ``(x, y)`` = canto inferior-esquerdo do ícone
    (convenção Kivy: y cresce para cima). ``size`` é a aresta do quadrado.

    ``color`` opcional — default ``BLOCK_ICON_OUTLINE`` (semelhante aos
    demais ícones de bloco, mas pode ser customizado para destaque
    quando o bloco da categoria Python estiver em estado :down).
    """
    from kivy.graphics import Ellipse

    s = size
    ctx = canvas if canvas is not None else widget.canvas
    stroke = color if color is not None else BLOCK_ICON_OUTLINE

    # Cubic Bezier — arco "cobra A": do canto inf-esq → topo-dir,
    # passando pelo centro com barriga (control points puxam para fora).
    snake_a = _cubic_bezier_points(
        p0=(x + 3,        y + s - 3),    # inf-esq
        p1=(x + 3,        y + s + 4),    # puxa p/ fora (esq-baixo)
        p2=(x + s - 3,    y - 4),        # puxa p/ fora (dir-cima)
        p3=(x + s - 3,    y + 3),        # sup-dir
    )
    # Espelho — "cobra B": canto sup-esq → inf-dir, passando pelo centro
    snake_b = _cubic_bezier_points(
        p0=(x + 3,        y + 3),        # sup-esq
        p1=(x + 3,        y - 4),
        p2=(x + s - 3,    y + s + 4),
        p3=(x + s - 3,    y + s - 3),    # inf-dir
    )

    with ctx:
        Color(*stroke)
        Line(points=snake_a, width=2.2, cap="round", joint="round")
        Line(points=snake_b, width=2.2, cap="round", joint="round")
        # Olhos (cabeças das cobras) — 2 dots pequenos nos topos
        # das curvas, reforçando a leitura de "duas cobras".
        eye_r = max(1.5, s * 0.08)
        Ellipse(
            pos=(x + s - 4 - eye_r, y + s - 4 - eye_r),
            size=(eye_r * 2, eye_r * 2),
        )
        Ellipse(
            pos=(x + 2, y + 2),
            size=(eye_r * 2, eye_r * 2),
        )


# --- Placeholder tracejado (estado de arraste — spec seção 5 regra 8) --


def draw_drag_placeholder(
    widget,
    width: float,
    height: float,
    amplitude: float = BLOCK_WAVE_AMPLITUDE,
    color=(1, 1, 1, 0.4),
) -> None:
    """Silhueta bandeirola tracejada — placeholder quando um bloco está
    sendo arrastado (spec seção 5 regra 8: "estado de arraste com
    sombra/placeholder tracejado").

    Diferente do bloco real, é apenas contorno (não fill) e tracejado.
    Cor padrão: branco 40% alpha.
    """
    segments_count = 12
    r = min(BLOCK_CORNER_RADIUS, width / 2, height / 2)

    outline_pts: list[float] = []
    # Top wave: i=0..segments_count
    for i in range(segments_count + 1):
        t = i / segments_count
        x = r + (width - 2 * r) * t
        y = -4 * amplitude * t * (1 - t)
        outline_pts.extend([x, y])
    # Right side
    outline_pts.extend([width, height - r])
    # Bottom wave (i=segments_count..0)
    for i in range(segments_count, -1, -1):
        t = i / segments_count
        x = r + (width - 2 * r) * t
        y = height + 4 * amplitude * t * (1 - t)
        outline_pts.extend([x, y])
    # Left side
    outline_pts.extend([0.0, r])

    with widget.canvas:
        Color(*color)
        Line(points=outline_pts, close=True, width=1.5,
             dash_length=4, dash_offset=2)