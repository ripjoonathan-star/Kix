# Kix

Engine de programação visual mobile-first em Python + Kivy. Inspirada em
[Pocket Code](https://www.catrobat.org/) / Catroid, mas com sistema de
blocos universal — uma única classe `KixBlock` cobre todos os blocos, e
usuários podem criar blocos em Python com o decorator `@kix_block`.

Estado atual: **M6** (CLI runner + renderizador PNG + 320+ blocos).

## Quickstart

```bash
git clone <repo> kix
cd kix
pip install -r Kix/requirements.txt        # Kivy 2.3.1, Pillow, pytest
python3 -m pytest tests/ -q                # roda a suíte (239 testes)
python3 -m Kix.main                        # abre o app
python3 -m Kix.cli demo --png out.png      # roda o demo sem display
```

> Requer Python 3.11+, Kivy 2.3.1, Pillow, display OpenGL (X11/Wayland/Windows/macOS)
> para o app; o CLI runner **funciona sem display**.
> Para Android: ver `BUILD_ANDROID.md` (buildozer + APK).

## Estrutura

```
Kix/
├── main.py              # Entrada do app
├── core/                # App, tema, paths, navegação
├── screens/             # Dashboard, Editor + tabs
│   └── tabs/            # Programação | Palco | Objetos | Recursos | Cenário
├── ui/                  # Widgets custom (botões, cards, app bar)
├── block_engine/        # KixBlock (universal), visual, behavior
├── blocks/              # 320+ blocos em 22 categorias
├── engine/              # Runtime: ctx, executor, services, decorator
├── projects/            # Modelo, serialização JSON, manager
└── assets/              # Ícones, fontes, imagens
```

## Funcionalidades

### UI (mobile-first)

- **Dashboard**: lista projetos salvos, cria novos, abre para editar
- **Editor** com 5 abas:
  - **Programação**: filtro por categoria, paleta horizontal, canvas vertical.
    Cada bloco tem botões `↑ ↓ ✎ ✕` — reordenar e editar inputs no canvas.
  - **Palco**: estado do sprite visualizado em tempo real + ▶ Play / ⏹ Stop / ↺ Reset.
  - **Objetos / Recursos / Cenário**: placeholders (M5).
- **Persistência**: projetos `.kix` em JSON versionado; estado do sprite
  (posição, rotação, tamanho, opacidade) é salvo após cada execução e
  restaurado na próxima.

### Engine (real, testada — 239 testes)

- **320+ blocos** em 22 categorias (Catroid-aligned).
- **Decorator `@kix_block`** para criar blocos novos em Python:

  ```python
  from Kix.engine.decorator import kix_block
  from Kix.core.theme import CAT_MATH

  @kix_block(id="my.ln2", category="math", color=CAT_MATH)
  def ln2(n: float) -> float:
      import math
      return math.log(n) / math.log(2)
  ```

- **Executor**: `BlockExecutor().run_block(block, ctx, inputs)` — compila
  `BlockBehavior.source` em `async def`, executa contra `RuntimeContext`.
- **SelfBinding**: `self.x = ...` resolve para input → sprite → ctx.
- **Scripts aninhados**: `control.repeat`/`forever`/`if`/`when_receive`
  aceitam `body=[block_dict, ...]` e rodam recursivamente.

### CLI runner (M6) — testável sem display

```bash
python3 -m Kix.cli demo --png out.png        # roda projeto demo → PNG
python3 -m Kix.cli run projeto.kix --png out.png --json out.json
python3 -m Kix.cli make-demo demo.kix        # gera projeto demo
python3 -m Kix.cli list-blocks               # lista os 320+ blocos
```

- Carrega `.kix` (JSON), monta `RuntimeContext`, executa blocos sequencialmente.
- Renderiza o palco (fundo + sprite rotacionado com tint/opacidade) para PNG.
- Emite estado final (sprite + variáveis + erros) em JSON.
- Perfeito para CI e para testar o engine em servidor sem GPU.

### Categorias de blocos (resumo)

| Categoria       | Qtd | O que cobre |
|-----------------|-----|-------------|
| motion          | 35  | Mover, girar, slide, ir para, etc. |
| looks           | 36  | Dizer, mostrar, esconder, opacidade, tamanho, animação |
| control         | 15  | Wait, repeat, forever, if, broadcast, clones, continue, break |
| sensing         | 47  | Touch, mouse, timer, cor, **GPS, NFC, bússola, inclinação, luz, proximidade, ruído, temperatura, umidade, pressão, face/OCR (stubs), fala** |
| device          | 25  | Vibrar, clipboard, keyboard, **Makey-Makey, hardware sensors** |
| math            | 43  | 23 trig/log/random + **20 operadores (+ − × ÷ mod pow, = ≠ < > ≤ ≥, e/ou/não, str ops)** |
| strings         | 12  | join, length, contém, replace, **str.eq/ne/lt/gt** |
| data            | 16  | Set/get/delete, listas (length, contains, index_of, replace, get) |
| network         | 33  | HTTP, TCP, WS, UDP, **NXT, Arduino (drivers stubs honestos)** |
| pen             | 8+  | Down, up, color, size, stamp, clear, **move_xy** |
| physics         | 14  | Walls, raycast, **gravidade** |
| storage         | 11  | Save/load nomeados, **tipados (number/bool), list_keys, clear, size** |
| + outras 10     |     | tilemap, spritesheet, ui, joystick, particles, scenes, AI, notifications, ar/vr, audio |

## Comandos úteis

```bash
# testes
python3 -m pytest tests/ -q                              # roda tudo (~0.5s)
python3 -m pytest tests/test_m5_expansion.py -v
python3 -m pytest tests/test_m6_cli_runner.py -v         # CLI runner + PNG

# UI
python3 -m Kix.main                                      # abre o app
KIX_USER_DATA=./tmp python3 -m Kix.main                  # custom user data dir

# CLI runner (M6) — testa sem display
python3 -m Kix.cli --help
python3 -m Kix.cli demo --png out.png
python3 -m Kix.cli run projeto.kix --png out.png --json out.json
python3 -m Kix.cli make-demo demo.kix
python3 -m Kix.cli list-blocks

# Inspecionar blocos
python3 -c "from Kix.blocks.builtin import ALL; print(f'{len(ALL)} blocos')"
```

## O que **NÃO** está implementado (fora do escopo M6)

Funcionalidades Catroid que continuam como stubs honestos ou não cobertas:

- **Reconhecimento de voz/fala real** — speech_to_text em Android.
- **Detecção de rosto / OCR** — requer ML Kit / Tesseract.
- **Câmera/vídeo ao vivo** — preview dentro do app.
- **NXT/Arduino/Makey-Makey drivers reais** — Bluetooth/USB HID precisam de
  módulos nativos (`pybluez`, `pyusb`).
- **Locais (i18n)** — só PT-BR.
- **Cloud variables** — variáveis sincronizadas com servidor.
- **Undo/Redo** — não tem.
- **Editor visual de nesting** — bodies de `if`/`repeat` funcionam via CLI/JSON
  mas o canvas não tem drag-and-drop para inserir blocos no body.
- **Gamepad externo** (somente touch/joystick virtual).
- **Buildozer / APK Android** — ver `BUILD_ANDROID.md`.

Tudo isso está marcado como `NotImplementedError` ou retorna valores neutros
quando invocado, em vez de mentir sobre funcionar.

## Marcos

- **M1**: modelo de bloco, executor, decoração, persistência.
- **M2**: 168 blocos em 19 categorias.
- **M3**: cobertura Catroid + decorator.
- **M4**: UI completa (Dashboard + Editor 5 abas + Run).
- **M5**: 320+ blocos (fórmula, sensors, hardware, gestos, dados,
  storage expandido), UI refinada (filtro de categoria, edição de inputs,
  reordenação, reset sprite), executor com scripts aninhados.
- **M6**: CLI runner (`python3 -m Kix.cli`) + renderizador PNG do palco
  via Pillow. Permite testar projetos `.kix` sem display — saídas em PNG
  e JSON. Sub-comandos: `run`, `demo`, `make-demo`, `list-blocks`.

## Licença

MIT.
