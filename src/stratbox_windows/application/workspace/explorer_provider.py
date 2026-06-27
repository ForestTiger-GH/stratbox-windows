from __future__ import annotations

from pathlib import Path
from typing import Protocol


class ExplorerProvider(Protocol):
    provider_id: str

    def exists(self, path: Path) -> bool: ...

    def is_dir(self, path: Path) -> bool: ...

    def list_children(self, directory: Path) -> tuple[Path, ...]: ...


class LocalWorkspaceExplorerProvider:
    provider_id = 'local_workspace'

    def exists(self, path: Path) -> bool:
        return path.exists()

    def is_dir(self, path: Path) -> bool:
        return path.is_dir()

    def list_children(self, directory: Path) -> tuple[Path, ...]:
        try:
            return tuple(directory.iterdir())
        except Exception:
            return tuple()
