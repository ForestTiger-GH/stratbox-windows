from __future__ import annotations

import os
import subprocess
from pathlib import Path


class PlatformServices:
    def open_path(self, path: str) -> None:
        target = Path(path)
        if not target.exists() and target.parent.exists():
            target = target.parent
        if os.name == 'nt':
            os.startfile(str(target))  # type: ignore[attr-defined]
        else:
            subprocess.Popen(['xdg-open', str(target)])

    def reveal_path(self, path: str) -> None:
        target = Path(path)
        reveal_target = target if target.is_dir() else target.parent
        if not reveal_target.exists():
            reveal_target = target
        if os.name == 'nt':
            os.startfile(str(reveal_target))  # type: ignore[attr-defined]
        else:
            subprocess.Popen(['xdg-open', str(reveal_target)])

    def copy_text(self, value: str) -> None:
        from PySide6.QtGui import QGuiApplication

        QGuiApplication.clipboard().setText(value)
