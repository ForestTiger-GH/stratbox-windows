from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    'README.md',
    'pyproject.toml',
    'appdock/manifest.json',
    'appdock/preset.json',
    'docs/architecture.md',
    'docs/development.md',
    'docs/appdock-integration.md',
    'tests/contracts/test_runtime_contracts.py',
    'tests/smoke/test_external_core_dependency.py',
    'tests/unit/test_paths.py',
    'src/stratbox_windows/application/logs/__init__.py',
    'src/stratbox_windows/application/logs/models.py',
    'src/stratbox_windows/application/logs/store.py',
    'src/stratbox_windows/application/logs/tail.py',
    'src/stratbox_windows/application/history/__init__.py',
    'src/stratbox_windows/application/history/persistence.py',
    'src/stratbox_windows/presentation/qt_desktop/panels/case_panel.py',
    'src/stratbox_windows/presentation/qt_desktop/panels/node_overview_panel.py',
    'src/stratbox_windows/presentation/qt_desktop/panels/assignments_panel.py',
    'src/stratbox_windows/presentation/qt_desktop/components/background_strip.py',
]
CHECK_IGNORE_PATHS = [
    'src/stratbox_windows/application/logs/models.py',
    'src/stratbox_windows/application/history/persistence.py',
    'tests/contracts/test_runtime_contracts.py',
]


def main() -> int:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            failures.append(f'missing required file: {rel}')
        else:
            print(f'OK file {rel}')
    if (ROOT / '.git').exists():
        for rel in CHECK_IGNORE_PATHS:
            result = subprocess.run(['git', 'check-ignore', '-v', rel], cwd=ROOT, text=True, capture_output=True)
            if result.returncode == 0:
                failures.append(f'gitignore hides source file: {rel} :: {result.stdout.strip()}')
            else:
                print(f'OK git-visible {rel}')
    if failures:
        print('\nRelease integrity failed:')
        for failure in failures:
            print(f'  - {failure}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
