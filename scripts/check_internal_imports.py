from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

CORE_MODULES = [
    'stratbox',
    'stratbox.base.filestore',
    'stratbox_windows.adapters.appdock.entry',
    'stratbox_windows.adapters.appdock.runtime_contracts',
    'stratbox_windows.runtime.bootstrap',
    'stratbox_windows.runtime.context',
    'stratbox_windows.application.scenarios.runner',
    'stratbox_windows.application.logs',
    'stratbox_windows.application.artifacts',
    'stratbox_windows.application.cases',
    'stratbox_windows.application.events',
    'stratbox_windows.application.assignments',
    'stratbox_windows.application.background',
    'stratbox_windows.application.history',
    'stratbox_windows.application.workspace.registry',
    'stratbox_windows.application.workspace.resolver',
]

GUI_MODULES = [
    'stratbox_windows.presentation.qt_desktop.main',
    'stratbox_windows.presentation.qt_desktop.shell.main_window',
    'stratbox_windows.presentation.qt_desktop.scenario_coordinator',
]


def _import_modules(modules: list[str]) -> list[str]:
    failures: list[str] = []
    for module in modules:
        try:
            importlib.import_module(module)
            print(f'OK   {module}')
        except Exception as exc:
            failures.append(f'{module}: {type(exc).__name__}: {exc}')
            print(f'FAIL {module}: {type(exc).__name__}: {exc}')
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description='Smoke-check Strategy Box Windows imports.')
    parser.add_argument('--core-only', action='store_true', help='Check only non-GUI imports.')
    args = parser.parse_args()

    failures = _import_modules(CORE_MODULES)
    if not args.core_only:
        failures.extend(_import_modules(GUI_MODULES))

    if failures:
        print('\nBroken imports:')
        for failure in failures:
            print(f'  - {failure}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
