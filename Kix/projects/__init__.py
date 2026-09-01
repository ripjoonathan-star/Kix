"""Sistema de projetos Kix: modelo, serialização e gerenciamento (.kix).

O formato `.kix` é um único arquivo JSON versionado. Assets (imagens, sons)
são referenciados por path relativo ao arquivo `.kix` e ficam em diretórios
irmãos — o JSON nunca embute binários, o que mantém diffs legíveis e
projetos versionáveis em git.

Estrutura do JSON:
    {
        "format": "kix",
        "version": 1,
        "name": "Meu Jogo",
        "created_at": "ISO-8601",
        "modified_at": "ISO-8601",
        "description": "...",
        "scenes":     [{ id, name, background, objects: [object_ids] }, ...],
        "objects":    [{ id, name, kind, image, scripts: [script_ids] }, ...],
        "scripts":    [{ id, trigger, blocks: [block_ids] }, ...],
        "blocks":     [KixBlock serializado, ...],
        "settings":   { width, height, orientation }
    }
"""

from Kix.projects.model import (
    KixProject,
    KixScene,
    KixObject,
    KixScript,
    ProjectSettings,
)
from Kix.projects.serializer import (
    KIX_FORMAT,
    KIX_VERSION,
    KixFormatError,
    from_dict,
    from_json,
    to_dict,
    to_json,
)
from Kix.projects.manager import ProjectManager, ProjectInfo, bulk_export

__all__ = [
    "KIX_FORMAT", "KIX_VERSION", "KixFormatError",
    "KixProject", "KixScene", "KixObject", "KixScript", "ProjectSettings",
    "to_json", "from_json", "to_dict", "from_dict",
    "ProjectManager", "ProjectInfo", "bulk_export",
]