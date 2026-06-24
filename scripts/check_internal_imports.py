from __future__ import annotations

import importlib

CRITICAL_MODULES = [
    'stratbox_windows.adapters.appdock.entry',
    'stratbox_windows.runtime.bootstrap',
    'stratbox_windows.presentation.qt_desktop.main',
    'stratbox_windows.presentation.qt_desktop.shell.main_window',
    'stratbox_windows.presentation.qt_desktop.scenario_coordinator',
    'stratbox_windows.application.scenarios.runner',
    'stratbox_windows.application.logs',
    'stratbox_windows.application.artifacts',
    'stratbox_windows.application.cases',
    'stratbox_windows.application.events',
    'stratbox_windows.application.assignments',
    'stratbox_windows.application.background',
    'stratbox_windows.application.history',
]


def main() -> int:
    failures: list[str] = []
    for module in CRITICAL_MODULES:
        try:
            importlib.import_module(module)
            print(f'OK   {module}')
        except Exception as exc:
            failures.append(f'{module}: {type(exc).__name__}: {exc}')
            print(f'FAIL {module}: {type(exc).__name__}: {exc}')
    if failures:
        print('\nBroken imports:')
        for failure in failures:
            print(f'  - {failure}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
