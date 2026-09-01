"""Diretórios do app e de projetos.

Resolvidos em runtime (não constantes) porque dependem do `user_data_dir`
do Kivy, que só fica disponível após `App.build()`.
"""

from __future__ import annotations

import os
from pathlib import Path


def projects_dir() -> Path:
    """Diretório onde os projetos do usuário são salvos."""
    from kivy.app import App

    base = Path(App.get_running_app().user_data_dir)
    path = base / "projects"
    path.mkdir(parents=True, exist_ok=True)
    return path


def assets_dir() -> Path:
    """Diretório de assets empacotados (ícones, fontes, ...)."""
    return Path(os.path.dirname(os.path.dirname(__file__))) / "assets"


def packages_dir() -> Path:
    """Diretório onde pacotes de blocos importados são instalados."""
    from kivy.app import App

    base = Path(App.get_running_app().user_data_dir)
    path = base / "packages"
    path.mkdir(parents=True, exist_ok=True)
    return path