from __future__ import annotations

import json
from pathlib import Path

import pytest

from stratbox_windows.adapters.appdock.runtime_contracts import (
    ACTIVATION_CONTEXT_CONTRACT_VERSION,
    load_activation_context,
)
from stratbox_windows.runtime.errors import AppConfigError


def _write(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    return path


def test_load_activation_context_reads_strict_contract_3(
    tmp_path: Path,
    appdock_activation_payload: dict,
) -> None:
    context = load_activation_context(_write(tmp_path / 'activation.json', appdock_activation_payload))

    assert context.contract_version == ACTIVATION_CONTEXT_CONTRACT_VERSION
    assert context.world_id == 'stratbox'
    assert context.active_surface_id == 'desktop'
    assert context.entry_view == 'scenario_chat'
    assert context.workspace.source_root.endswith('stratbox-windows/payload')
    assert context.workspace.user_workspace_root.endswith('workspace')
    assert context.workspace.source_location_profile == 'source_location_remote'
    assert context.workspace.content_runtime_profile == 'content_runtime_sealed_materialized'
    assert context.provided_system_dirs.user_private_system_dir is not None
    assert context.provided_system_dirs.user_private_system_dir.kind == 'user_local'
    assert context.runtime_package_by_binding_id('stratbox-core-python').package_id == 'stratbox'
    assert context.runtime_package_by_binding_id('stratbox-windows-python').package_id == 'stratbox-windows'
    assert context.available_route_groups == ('workspace', 'logs')


def test_load_activation_context_rejects_legacy_contract(
    tmp_path: Path,
    appdock_activation_payload: dict,
) -> None:
    appdock_activation_payload['contract_version'] = '1.0'

    with pytest.raises(AppConfigError, match='requires 3.0'):
        load_activation_context(_write(tmp_path / 'activation.json', appdock_activation_payload))


def test_load_activation_context_rejects_legacy_workspace_and_package_mounts(
    tmp_path: Path,
    appdock_activation_payload: dict,
) -> None:
    appdock_activation_payload['workspace']['primary_root'] = appdock_activation_payload['workspace'].pop('source_root')
    appdock_activation_payload['package_mounts'] = []

    with pytest.raises(AppConfigError, match='unsupported fields'):
        load_activation_context(_write(tmp_path / 'activation.json', appdock_activation_payload))


def test_load_activation_context_requires_current_workspace_fields(
    tmp_path: Path,
    appdock_activation_payload: dict,
) -> None:
    appdock_activation_payload['workspace'].pop('user_workspace_root')

    with pytest.raises(AppConfigError, match='misses user_workspace_root'):
        load_activation_context(_write(tmp_path / 'activation.json', appdock_activation_payload))


def test_load_activation_context_rejects_invalid_runtime_package_digest(
    tmp_path: Path,
    appdock_activation_payload: dict,
) -> None:
    appdock_activation_payload['runtime_packages'][0]['payload_digest'] = 'bad'

    with pytest.raises(AppConfigError, match='SHA-256'):
        load_activation_context(_write(tmp_path / 'activation.json', appdock_activation_payload))
