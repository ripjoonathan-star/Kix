"""Gerenciador de projetos — CRUD + import/export de `.kix`."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from Kix.projects.model import KixProject
from Kix.projects.serializer import KixFormatError, from_json, to_json


@dataclass
class ProjectInfo:
    """Metadados para a lista do Dashboard."""

    name: str
    path: Path
    modified_at: str
    size_bytes: int

    @classmethod
    def from_path(cls, path: Path) -> "ProjectInfo":
        stat = path.stat()
        return cls(
            name=path.stem,
            path=path,
            modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            size_bytes=stat.st_size,
        )


class ProjectManager:
    """Gerencia projetos salvos em um diretório (default: user_data_dir/projects).

    Cada projeto é um único arquivo `.kix` (JSON). Assets referenciados por
    path relativo ficam em diretórios vizinhos, fora do escopo deste manager.
    """

    def __init__(self, base_dir: Path | None = None):
        if base_dir is None:
            # Import lazy: kivy pode não estar inicializado em testes
            try:
                from Kix.core.paths import projects_dir
                self.base_dir = projects_dir()
            except Exception:
                self.base_dir = Path.home() / ".kix" / "projects"
        else:
            self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # --- Helpers ----------------------------------------------------------
    def _path_for(self, name: str) -> Path:
        """Path completo para o arquivo .kix de `name` (sem extensão)."""
        if not name or not name.strip():
            raise ValueError("Nome do projeto vazio")
        if name.endswith(".kix"):
            name = name[:-4]
        # normaliza: sem '/', sem espaços extras
        name = name.strip().replace("/", "_").replace("\\", "_")
        return self.base_dir / f"{name}.kix"

    def _safe_overwrite_target(self, name: str) -> Path:
        target = self._path_for(name)
        if target.exists():
            raise FileExistsError(f"Projeto '{name}' já existe em {target}")
        return target

    # --- Listagem ---------------------------------------------------------
    def list(self) -> list[ProjectInfo]:
        """Retorna metadados de todos os projetos no diretório."""
        infos: list[ProjectInfo] = []
        for p in sorted(self.base_dir.glob("*.kix")):
            try:
                infos.append(ProjectInfo.from_path(p))
            except OSError:
                continue
        return infos

    def exists(self, name: str) -> bool:
        return self._path_for(name).exists()

    # --- Create / Save / Load ---------------------------------------------
    def create(self, name: str, *, template: KixProject | None = None) -> KixProject:
        """Cria projeto novo. Falha se nome já existir."""
        target = self._safe_overwrite_target(name)
        project = template or KixProject(name=name)
        project.name = name
        self.save(project)
        return project

    def save(self, project: KixProject) -> Path:
        """Persiste o projeto em seu .kix."""
        project.touch()
        target = self._path_for(project.name)
        target.write_text(to_json(project), encoding="utf-8")
        return target

    def load(self, name: str) -> KixProject:
        """Carrega projeto do disco pelo nome."""
        path = self._path_for(name)
        if not path.exists():
            raise FileNotFoundError(f"Projeto '{name}' não encontrado em {path}")
        return self._load_from_path(path)

    def load_path(self, path: Path | str) -> KixProject:
        """Carrega projeto a partir de qualquer path .kix."""
        return self._load_from_path(Path(path))

    def _load_from_path(self, path: Path) -> KixProject:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            raise KixFormatError(f"Não consegui ler {path}: {e}") from e
        return from_json(text)

    # --- Rename / Duplicate / Delete --------------------------------------
    def rename(self, old_name: str, new_name: str) -> Path:
        src = self._path_for(old_name)
        if not src.exists():
            raise FileNotFoundError(f"Projeto '{old_name}' não encontrado")
        dst = self._safe_overwrite_target(new_name)
        project = self.load(old_name)
        project.name = new_name
        # salva em dst, depois remove src
        self.save(project)  # escreve em dst
        # garantir remoção mesmo se save tiver escrito em src por race
        if src.exists() and src != dst:
            src.unlink()
        return dst

    def duplicate(self, source_name: str, new_name: str) -> KixProject:
        src = self._path_for(source_name)
        if not src.exists():
            raise FileNotFoundError(f"Projeto '{source_name}' não encontrado")
        project = self.load(source_name)
        project.name = new_name
        # renova IDs para evitar colisões com o original
        self._regenerate_ids(project)
        return self.create(new_name, template=project)

    def delete(self, name: str) -> None:
        path = self._path_for(name)
        if not path.exists():
            raise FileNotFoundError(f"Projeto '{name}' não encontrado")
        path.unlink()

    # --- Import / Export --------------------------------------------------
    def export(self, name: str, dest: Path | str) -> Path:
        """Copia o .kix do projeto `name` para `dest` (path externo)."""
        src = self._path_for(name)
        if not src.exists():
            raise FileNotFoundError(f"Projeto '{name}' não encontrado")
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        return Path(shutil.copy2(src, dest))

    def import_project(self, source: Path | str, *, new_name: str | None = None) -> KixProject:
        """Importa um .kix de fora para o diretório gerenciado.

        Valida formato/versão. Se `new_name` for dado, renomeia antes de
        salvar (útil para evitar colisão com projeto existente).
        """
        source = Path(source)
        if not source.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {source}")
        project = self._load_from_path(source)
        if new_name:
            project.name = new_name
        target = self._path_for(project.name)
        if target.exists():
            raise FileExistsError(
                f"Já existe projeto '{project.name}' no diretório gerenciado"
            )
        self.save(project)
        return project

    # --- Utilitários internos --------------------------------------------
    @staticmethod
    def _regenerate_ids(project: KixProject) -> None:
        """Regenera IDs de scene/object/script ao duplicar, preservando as referências."""
        from Kix.projects.model import _new_id

        scene_map = {s.id: _new_id("scn") for s in project.scenes}
        object_map = {o.id: _new_id("obj") for o in project.objects}
        script_map = {s.id: _new_id("scr") for s in project.scripts}

        for scene in project.scenes:
            scene.id = scene_map[scene.id]
            scene.objects = [object_map[oid] for oid in scene.objects if oid in object_map]
        for obj in project.objects:
            obj.id = object_map[obj.id]
            obj.scripts = [script_map[sid] for sid in obj.scripts if sid in script_map]
        for script in project.scripts:
            script.id = script_map[script.id]

    def __repr__(self) -> str:
        return f"ProjectManager(base_dir={self.base_dir!r})"


def bulk_export(manager: ProjectManager, names: Iterable[str], dest_dir: Path | str) -> list[Path]:
    """Exporta vários projetos em lote para `dest_dir`."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    out: list[Path] = []
    for name in names:
        out.append(manager.export(name, dest_dir / f"{name}.kix"))
    return out