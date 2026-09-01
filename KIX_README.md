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
pip install -r Kix/requirements.txt        # Kivy 2.3.1, pytest
python3 -m pytest tests/ -q                # roda a suíte (~222 testes)
python3 -m Kix.main                        # abre o app
```

## Estado atual (M5)

- 320+ blocos em 22 categorias (fórmula, sensors, hardware, gestos, dados, etc.)
- UI Kivy com Dashboard + Editor (5 abas) + execução real
- Executor + decorator + serialização de projetos
- 222 testes passando

## Estrutura

Ver `Kix/README.md`.

## Licença

MIT.
