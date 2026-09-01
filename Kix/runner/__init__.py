"""Runner headless de projetos .kix.

Carrega um `KixProject` (JSON), monta um `RuntimeContext`, executa
os blocos (stateful scripts) e devolve o estado final para o caller
ou para a CLI renderizar.
"""

from Kix.runner.project_runner import (
    ProjectRunResult,
    run_project,
    run_project_dict,
    run_project_path,
)

__all__ = ["run_project", "run_project_dict", "run_project_path", "ProjectRunResult"]
