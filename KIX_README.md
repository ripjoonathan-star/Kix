# Kix — Engine de Programação Visual (Python + Kivy)

Engine mobile-first de programação visual em Python + Kivy, inspirada em
[Pocket Code](https://www.catrobat.org/) / Catroid. Sistema universal
de blocos — uma única classe `KixBlock` cobre todos os 320+ blocos —
mais um decorator `@kix_block` que permite criar novos blocos em
Python com tipos e visual gerados automaticamente.

> Veja `Kix/README.md` para documentação completa. Este README raiz
> existe só para apresentação no topo do repositório.

## Quickstart

```bash
pip install -r Kix/requirements.txt        # Kivy 2.3.1, Pillow, pytest
python3 -m pytest tests/ -q                # roda a suíte (239 testes)
python3 -m Kix.main                        # abre o app Kivy
python3 -m Kix.cli demo --png out.png      # roda o projeto demo sem display
python3 -m Kix.cli run projeto.kix --png out.png
```

## Estado atual (M6)

- 320+ blocos em 22 categorias (fórmula, sensors, hardware, gestos, dados, etc.)
- UI Kivy com Dashboard + Editor (5 abas) + execução real
- Executor + decorator + serialização de projetos
- **CLI runner + renderizador PNG** (M6): roda projetos `.kix` headless,
  desenha o palco para PNG via Pillow — testável sem display.
- 239 testes passando

## Estrutura

Ver `Kix/README.md`.

## Licença

MIT.
