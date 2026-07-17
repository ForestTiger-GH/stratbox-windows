from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def build_activation_context_payload(tmp_path: Path | None = None) -> dict:
    root = tmp_path or Path('C:/StrategyBox')
    install_root = root / 'install'
    package_root = install_root / 'appdock-packages'
    source_root = package_root / 'packages' / 'stratbox-windows' / 'payload'
    return {
        'contract_version': '3.0',
        'generated_at_utc': '2026-07-17T00:00:00Z',
        'world': {
            'world_id': 'stratbox',
            'display_name': 'Strategy Box',
        },
        'active_surface': {
            'surface_id': 'desktop',
            'entry_view': 'scenario_chat',
            'declared_views': ['scenario_chat', 'workspace'],
        },
        'activation': {
            'attach_mode': 'remote',
            'degraded_launch': False,
        },
        'source_revision': {
            'ref_kind': 'branch',
            'ref': 'main',
            'commit': 'abc123',
            'sync_mode': 'snapshot',
        },
        'workspace': {
            'install_root': str(install_root),
            'user_workspace_root': str(root / 'workspace'),
            'system_root': str(install_root / 'appdock-system'),
            'source_root': str(source_root),
            'package_root': str(package_root),
            'data_root_status': 'available',
            'data_root_path': str(root / 'data'),
            'source_location_profile': 'source_location_remote',
            'content_runtime_profile': 'content_runtime_sealed_materialized',
        },
        'provided_system_dirs': {
            'install_root_system_dir': {
                'kind': 'install_root',
                'directory_name': 'appdock-system',
                'path': str(install_root / 'appdock-system'),
                'provider_class': 'filesystem',
            },
            'user_private_system_dir': {
                'kind': 'user_local',
                'directory_name': 'Strategy Box',
                'path': str(root / 'user-private-system'),
                'provider_class': 'filesystem',
            },
        },
        'refs': {
            'health_snapshot_ref': str(install_root / 'refs' / 'health.json'),
            'user_state_ref': str(install_root / 'refs' / 'user.json'),
            'session_ref': str(install_root / 'refs' / 'session.json'),
            'active_session_ref': str(install_root / 'refs' / 'active-session.json'),
            'runtime_state_ref': str(install_root / 'refs' / 'runtime.json'),
        },
        'node': {
            'node_id': 'node-1',
            'node_created_at_utc': '2026-07-17T00:00:00Z',
            'host_name': 'strategy-host',
        },
        'user': {
            'user_id': 'user-1',
            'account_name': 'analyst',
        },
        'session': {
            'session_id': 'session-1',
            'session_started_at_utc': '2026-07-17T00:00:00Z',
        },
        'available_route_groups': ['workspace', 'logs'],
        'runtime_packages': [
            {
                'binding_id': 'stratbox-core-python',
                'package_id': 'stratbox',
                'package_version': '0.2.1',
                'binding_profile': 'runtime_binding_python_distribution',
                'environment_id': 'world',
                'relative_path': 'packages/stratbox/payload',
                'payload_digest': 'a' * 64,
                'specification': {},
            },
            {
                'binding_id': 'stratbox-windows-python',
                'package_id': 'stratbox-windows',
                'package_version': '0.1.0',
                'binding_profile': 'runtime_binding_python_distribution',
                'environment_id': 'world',
                'relative_path': 'packages/stratbox-windows/payload',
                'payload_digest': 'b' * 64,
                'specification': {},
                'platform_profile': {
                    'system': 'windows',
                    'architecture': 'x64',
                },
            },
        ],
    }


@pytest.fixture
def appdock_activation_payload(tmp_path: Path) -> dict:
    return copy.deepcopy(build_activation_context_payload(tmp_path))
