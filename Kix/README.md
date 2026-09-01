# Kix

Engine de programação visual mobile-first em Python + Kivy. Inspirada em
[Pocket Code](https://www.catrobat.org/) / Catroid, mas com sistema de
blocos universal — uma única classe `KixBlock` cobre todos os blocos, e
usuários podem criar blocos em Python com o decorator `@kix_block`.

Estado atual: **M5** (UI funcional + execução real + 320+ blocos).

## Quickstart

```bash
git clone <repo> kix
cd kix
pip install -r Kix/requirements.txt        # Kivy 2.3.1, pytest
python3 -m pytest tests/ -q                # roda a suíte (deve passar)
python3 -m Kix.main                        # abre o app
```

> Requer Python 3.11+, Kivy 2.3.1, display OpenGL (X11/Wayland/Windows/macOS).
> Para Android: empacotar com Buildozer (fora deste marco).

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

### Engine (real, testada — 222 testes)

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
python3 -m pytest tests/ -q                  # roda tudo (~0.5s)
python3 -m pytest tests/test_m5_expansion.py -v

# UI
python3 -m Kix.main                          # abre o app
KIX_USER_DATA=./tmp python3 -m Kix.main      # custom user data dir

# Inspecionar blocos
python3 -c "from Kix.blocks.builtin import ALL; print(f'{len(ALL)} blocos')"
```

## O que **NÃO** está implementado (fora do escopo M5)

Funcionalidades Catroid que continuam como stubs honestos ou não cobertas:

- **Reconhecimento de voz/fala real** — speech_to_text em Android.
- **Detecção de rosto / OCR** — requer ML Kit / Tesseract.
- **Câmera/vídeo ao vivo** — preview dentro do app.
- **NXT/Arduino/Makey-Makey drivers reais** — Bluetooth/USB HID precisam de
  módulos nativos (`pybluez`, `pyusb`).
- **Locais (i18n)** — só PT-BR.
- **Cloud variables** — variáveis sincronizadas com servidor.
- **Undo/Redo** — não tem.
- **Drag-and-drop de blocos para dentro do body de `if`/`repeat`** — bodies
  ficam como lista vazia até uma UI de nesting ser construída (M6).
- **Gamepad externo** (somente touch/joystick virtual).
- **Buildozer / APK Android** — requer ambiente separado.

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

## Licença

MIT.
