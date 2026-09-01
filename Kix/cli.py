"""CLI runner — roda projetos `.kix` sem precisar de display Kivy.

Uso:
    python3 -m Kix.cli run <projeto.kix> [--png out.png] [--json out.json] [--quiet]
    python3 -m Kix.cli demo                       # roda um projeto embutido
    python3 -m Kix.cli make-demo path.kix         # gera um projeto demo
    python3 -m Kix.cli list-blocks                # lista todos os blocos disponíveis

Saída:
- Imprime sumário do `ProjectRunResult` em stdout.
- Com `--png`, renderiza o palco para um PNG.
- Com `--json`, escreve o estado final (sprite + variáveis) em JSON.

Pensado para CI e para o usuário testar o engine em ambiente sem GPU.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from Kix import __version__
from Kix.runner import ProjectRunResult, run_project_path
from Kix.runner.demo import demo_project, write_demo


# --- helpers --------------------------------------------------------------
def _print_sprite_state(sprite, fh) -> None:
    if sprite is None:
        fh.write("  (sem sprite ativo)\n")
        return
    x, y = sprite.position
    fh.write(
        f"  posição=({x:.1f}, {y:.1f})  rotação={sprite.rotation:.1f}°  "
        f"escala={sprite.scale:.2f}  opacidade={sprite.opacity:.2f}\n"
    )


def _write_json(result: ProjectRunResult, out_path: Path) -> None:
    sprite = result.sprite
    payload: dict[str, Any] = {
        "project": result.project_name,
        "blocks_run": result.blocks_run,
        "blocks_failed": result.blocks_failed,
        "variables": result.variables,
        "errors": result.errors,
        "log": result.log,
        "sprite": None,
    }
    if sprite is not None:
        payload["sprite"] = {
            "name": sprite.name,
            "position": list(sprite.position),
            "rotation": sprite.rotation,
            "scale": sprite.scale,
            "opacity": sprite.opacity,
            "visible": sprite.visible,
            "tint": list(sprite.tint),
        }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


# --- subcomandos ----------------------------------------------------------
def cmd_run(args: argparse.Namespace) -> int:
    src = Path(args.path)
    if not src.exists():
        print(f"Arquivo não encontrado: {src}", file=sys.stderr)
        return 2

    try:
        result = run_project_path(src)
    except Exception as exc:
        print(f"Erro ao rodar {src}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"Projeto: {result.project_name}")
        print(f"Sprite:  {result.sprite.name if result.sprite else '(nenhum)'}")
        _print_sprite_state(result.sprite, sys.stdout)
        print(f"Blocos:  {result.blocks_run} ok, {result.blocks_failed} falharam")
        if result.variables:
            print("Variáveis:")
            for k, v in result.variables.items():
                print(f"  {k} = {v!r}")
        if result.errors:
            print("Erros:", file=sys.stderr)
            for err in result.errors:
                print(f"  {err}", file=sys.stderr)
            return 1

    if args.json:
        _write_json(result, Path(args.json))
        if not args.quiet:
            print(f"Estado → {args.json}")

    if args.png:
        from Kix.render import render_ctx_to_png
        from Kix.runner import run_project
        from Kix.projects.model import KixProject
        from Kix.projects.serializer import from_json
        from Kix.engine.ctx import make_ctx

        text = src.read_text(encoding="utf-8")
        project = from_json(text)
        # Re-executa dentro de um ctx fresco para conseguir renderizar o estado final.
        # (alternativa: expor `ctx` no ProjectRunResult — mas isso muda a API)
        ctx = make_ctx(screen_width=project.settings.width,
                       screen_height=project.settings.height)
        from Kix.runner.project_runner import _apply_scene_bg
        _apply_scene_bg(project, ctx)
        # Aplica o estado do último run para o render reproduzir visualmente
        if result.sprite is not None and ctx.stage.active is not None:
            ctx.stage.active.position = result.sprite.position
            ctx.stage.active.rotation = result.sprite.rotation
            ctx.stage.active.scale = result.sprite.scale
            ctx.stage.active.opacity = result.sprite.opacity
            ctx.stage.active.visible = result.sprite.visible
            ctx.stage.active.tint = result.sprite.tint

        out = render_ctx_to_png(ctx, args.png)
        if not args.quiet:
            print(f"PNG   → {out}")

    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    project = demo_project()
    from Kix.runner import run_project

    import asyncio
    result = asyncio.run(run_project(project))
    if not args.quiet:
        print(result.summary())

    if args.png:
        from Kix.render import render_ctx_to_png
        ctx = make_ctx_for(project)
        # reaplica o bg da cena (perdido quando make_ctx recria o stage)
        from Kix.runner.project_runner import _apply_scene_bg
        _apply_scene_bg(project, ctx)
        if result.sprite is not None and ctx.stage.active is not None:
            ctx.stage.active.position = result.sprite.position
            ctx.stage.active.rotation = result.sprite.rotation
            ctx.stage.active.scale = result.sprite.scale
            ctx.stage.active.opacity = result.sprite.opacity
            ctx.stage.active.visible = result.sprite.visible
            ctx.stage.active.tint = result.sprite.tint
        out = render_ctx_to_png(ctx, args.png)
        if not args.quiet:
            print(f"PNG   → {out}")
    return 0


def make_ctx_for(project):
    from Kix.engine.ctx import make_ctx
    return make_ctx(screen_width=project.settings.width,
                    screen_height=project.settings.height)


def cmd_make_demo(args: argparse.Namespace) -> int:
    out = write_demo(Path(args.path))
    if not args.quiet:
        print(f"Demo gravado em {out}")
    return 0


def cmd_list_blocks(args: argparse.Namespace) -> int:
    from Kix.blocks.builtin import ALL
    by_cat: dict[str, list[str]] = {}
    for b in ALL:
        by_cat.setdefault(b.category, []).append(b.id)
    print(f"Total: {len(ALL)} blocos")
    for cat in sorted(by_cat):
        ids = by_cat[cat]
        print(f"[{cat}] ({len(ids)})")
        for bid in sorted(ids):
            print(f"  - {bid}")
    return 0


# --- argparse --------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python3 -m Kix.cli",
        description="Kix CLI — roda projetos .kix sem display",
    )
    p.add_argument("--version", action="version", version=f"Kix {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Roda um projeto .kix")
    p_run.add_argument("path", help="Caminho do arquivo .kix")
    p_run.add_argument("--png", metavar="OUT.png", help="Renderiza o palco para PNG")
    p_run.add_argument("--json", metavar="OUT.json", help="Salva estado final em JSON")
    p_run.add_argument("--quiet", "-q", action="store_true", help="Só imprime PNG/JSON, sem log")
    p_run.set_defaults(func=cmd_run)

    p_demo = sub.add_parser("demo", help="Roda um projeto demo embutido")
    p_demo.add_argument("--png", metavar="OUT.png", help="Renderiza o palco para PNG")
    p_demo.add_argument("--quiet", "-q", action="store_true", help="Suprime log")
    p_demo.set_defaults(func=cmd_demo)

    p_make = sub.add_parser("make-demo", help="Grava o projeto demo em .kix")
    p_make.add_argument("path", help="Caminho destino (.kix)")
    p_make.add_argument("--quiet", "-q", action="store_true", help="Suprime log")
    p_make.set_defaults(func=cmd_make_demo)

    p_list = sub.add_parser("list-blocks", help="Lista todos os blocos disponíveis")
    p_list.set_defaults(func=cmd_list_blocks)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
