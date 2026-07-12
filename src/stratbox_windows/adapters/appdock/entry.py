"""Canonical AppDock-facing module entry for Strategy Box Windows.

The entry keeps AppDock integration at one boundary. Until AppDock installs
auxiliary Python sources as runtime packages, it can also activate the declared
``stratbox`` package mount directly from the activation context.
"""

from __future__ import annotations

import sys
from pathlib import Path

from stratbox_windows.adapters.appdock.runtime_contracts import load_activation_context_from_env


def _activate_stratbox_package_mount() -> None:
    """Expose the AppDock-materialized ``stratbox`` source to Python when needed."""
    context = load_activation_context_from_env()
    if context is None:
        return

    package_root = Path(context.workspace.package_root).expanduser().resolve()
    mount = next((item for item in context.package_mounts if item.mount_id == 'stratbox'), None)
    if mount is None:
        return

    mounted_root = (package_root / mount.relative_path).resolve()
    if mounted_root != package_root and package_root not in mounted_root.parents:
        return

    for candidate in (mounted_root / 'src', mounted_root):
        if (candidate / 'stratbox').is_dir():
            value = str(candidate)
            if value not in sys.path:
                sys.path.insert(0, value)
            return


def main(argv: list[str] | None = None) -> int:
    _activate_stratbox_package_mount()
    from stratbox_windows.__main__ import main as app_main

    return app_main(argv, launch_origin='appdock')


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
