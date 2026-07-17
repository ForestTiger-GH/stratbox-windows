"""Canonical AppDock-facing module entry for Strategy Box Windows."""

from __future__ import annotations

import sys

from stratbox_windows.adapters.appdock.runtime_contracts import (
    AppActivationContext,
    load_activation_context_from_env,
)
from stratbox_windows.runtime.errors import AppConfigError

STRATBOX_CORE_BINDING_ID = 'stratbox-core-python'
STRATBOX_WINDOWS_BINDING_ID = 'stratbox-windows-python'
PYTHON_DISTRIBUTION_BINDING_PROFILE = 'runtime_binding_python_distribution'


def validate_appdock_runtime_contract(context: AppActivationContext) -> None:
    """Confirm the manifest-owned runtime graph before entering application code."""

    if context.world_id != 'stratbox':
        raise AppConfigError(
            f'AppDock activation context targets unexpected world: {context.world_id}; expected stratbox'
        )
    if context.active_surface_id != 'desktop':
        raise AppConfigError(
            f'AppDock activation context targets unexpected surface: '
            f'{context.active_surface_id}; expected desktop'
        )

    core = context.require_runtime_package(
        STRATBOX_CORE_BINDING_ID,
        package_id='stratbox',
        binding_profile=PYTHON_DISTRIBUTION_BINDING_PROFILE,
    )
    desktop = context.require_runtime_package(
        STRATBOX_WINDOWS_BINDING_ID,
        package_id='stratbox-windows',
        binding_profile=PYTHON_DISTRIBUTION_BINDING_PROFILE,
    )
    if core.environment_id != desktop.environment_id:
        raise AppConfigError(
            'Strategy Box core and desktop runtime bindings must share one AppDock environment'
        )


def main(argv: list[str] | None = None) -> int:
    try:
        context = load_activation_context_from_env()
        if context is None:
            raise AppConfigError('AppDock activation context is required for the AppDock entrypoint')
        validate_appdock_runtime_contract(context)
    except AppConfigError as exc:
        print(f'ERROR: {exc}')
        return 2

    from stratbox_windows.__main__ import main as app_main

    return app_main(argv, launch_origin='appdock')


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))


__all__ = [
    'PYTHON_DISTRIBUTION_BINDING_PROFILE',
    'STRATBOX_CORE_BINDING_ID',
    'STRATBOX_WINDOWS_BINDING_ID',
    'main',
    'validate_appdock_runtime_contract',
]
