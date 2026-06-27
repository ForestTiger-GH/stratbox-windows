"""Информация о версии и Git-состоянии локального product tree."""

from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class VersionInfo:
    """Краткая информация о текущей копии приложения."""

    product_root: str
    branch: str = "unknown"
    commit: str = "unknown"
    commit_short: str = "unknown"
    dirty: bool = False
    last_commit_time: str = "unknown"

    def to_dict(self) -> dict[str, object]:
        """Преобразует сведения о версии в словарь."""
        return asdict(self)


def _git(product_root: Path, *args: str) -> str:
    """Выполняет git-команду и возвращает stdout."""
    completed = subprocess.run(
        ["git", "-C", str(product_root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    return completed.stdout.strip()


def get_version_info(product_root: Path) -> VersionInfo:
    """Возвращает Git-сведения, если Git доступен."""
    try:
        branch = _git(product_root, "rev-parse", "--abbrev-ref", "HEAD")
        commit = _git(product_root, "rev-parse", "HEAD")
        commit_short = _git(product_root, "rev-parse", "--short", "HEAD")
        status = _git(product_root, "status", "--porcelain")
        last_commit_time = _git(product_root, "log", "-1", "--format=%ci")
        return VersionInfo(
            product_root=str(product_root),
            branch=branch or "unknown",
            commit=commit or "unknown",
            commit_short=commit_short or "unknown",
            dirty=bool(status),
            last_commit_time=last_commit_time or "unknown",
        )
    except Exception:
        return VersionInfo(product_root=str(product_root))
