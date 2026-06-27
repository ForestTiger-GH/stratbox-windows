"""Точка входа для запуска Strategy Box Windows командой ``python -m stratbox_windows``."""

from __future__ import annotations

import argparse
import json
import sys

from stratbox_windows.runtime.errors import AppConfigError, AppError, AppStartupError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='python -m stratbox_windows',
        description='Strategy Box Windows desktop shell',
    )
    parser.add_argument('--no-gui', action='store_true', help='Run service command without opening GUI.')
    parser.add_argument('--diagnose', action='store_true', help='Run AppDock preflight diagnostics and print JSON result.')
    parser.add_argument(
        '--standalone-dev-root',
        default=None,
        help='Explicit selector path for standalone developer launch outside AppDock activation context.',
    )
    return parser


def _load_runtime_components() -> tuple:
    from stratbox_windows.runtime.context import build_app_context
    from stratbox_windows.application.operations.catalog.registry import build_operation_registry
    from stratbox_windows.application.operations.execution.runner import run_operation_by_id

    return build_app_context, build_operation_registry, run_operation_by_id


def _dependency_startup_error(exc: ModuleNotFoundError) -> AppStartupError:
    if exc.name == 'stratbox':
        return AppStartupError(
            'Strategy Box core runtime dependency is missing. '
            'AppDock must install the external package `stratbox` into the active runtime environment '
            'before the desktop surface can start.'
        )
    return AppStartupError(f'Failed to load startup dependency: {exc}')


def main(argv: list[str] | None = None, *, launch_origin: str = 'standalone') -> int:
    args = _build_parser().parse_args(argv)
    allow_missing_runtime_dependencies = bool(args.diagnose or args.no_gui)

    try:
        build_app_context, build_operation_registry, run_operation_by_id = _load_runtime_components()
        context = build_app_context(
            standalone_dev_root=args.standalone_dev_root,
            launch_origin=launch_origin,
            allow_missing_runtime_dependencies=allow_missing_runtime_dependencies,
        )
        registry = build_operation_registry(context)
    except ModuleNotFoundError as exc:
        error = _dependency_startup_error(exc)
        print(f'ERROR: {error}')
        return 2
    except AppConfigError as exc:
        print(f'ERROR: {exc}')
        return 2
    except AppError as exc:
        print(f'ERROR: {exc}')
        return 2

    if args.diagnose:
        result = run_operation_by_id(
            'system.diagnostics',
            registry=registry,
            context=context,
            params={'mode': 'appdock_preflight'},
        )
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 2

    if args.no_gui:
        result = run_operation_by_id('system.diagnostics', registry=registry, context=context, params={})
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 2

    try:
        from stratbox_windows.presentation.qt_desktop.main import run_gui
    except ModuleNotFoundError as exc:
        error = _dependency_startup_error(exc)
        print(f'ERROR: {error}')
        return 2
    except AppError as exc:
        print(f'ERROR: {exc}')
        return 2

    return run_gui(context)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
