from __future__ import annotations

import json
from pathlib import Path

import pytest

from stratbox_windows.adapters.appdock.runtime_contracts import load_activation_context
from stratbox_windows.runtime.errors import AppConfigError


def _payload() -> dict:
    return {
        "contract_version": "1.0",
        "generated_at_utc": "2026-07-12T00:00:00Z",
        "world": {
            "world_id": "stratbox",
            "display_name": "Strategy Box",
        },
        "active_surface": {
            "surface_id": "desktop",
            "entry_view": "scenario_chat",
            "declared_views": ["scenario_chat", "workspace"],
        },
        "activation": {
            "attach_mode": "local",
            "degraded_launch": False,
        },
        "source_revision": {
            "ref_kind": "branch",
            "ref": "main",
            "commit": "abc123",
            "sync_mode": "snapshot",
        },
        "workspace": {
            "install_root": "C:/StrategyBox",
            "system_root": "C:/StrategyBox/appdock-system",
            "package_root": "C:/StrategyBox/appdock-packages",
            "data_root_status": "configured",
            "data_root_path": "D:/BusinessData",
            "primary_root": "C:/StrategyBox/appdock-packages/repositories/primary",
            "primary_source_location_profile": "source_location_remote",
            "primary_content_runtime_profile": "content_runtime_managed_editable",
        },
        "provided_system_dirs": {
            "install_root_system_dir": {
                "kind": "install_root",
                "directory_name": "system",
                "path": "C:/StrategyBox/appdock-system",
                "provider_class": "filesystem",
            }
        },
        "refs": {
            "health_snapshot_ref": "C:/StrategyBox/refs/health.json",
            "user_state_ref": "C:/StrategyBox/refs/user.json",
            "session_ref": "C:/StrategyBox/refs/session.json",
            "active_session_ref": "C:/StrategyBox/refs/active_session.json",
            "runtime_state_ref": "C:/StrategyBox/refs/runtime.json",
            "cleanup_registry_ref": "C:/StrategyBox/refs/cleanup.json",
        },
        "node": {
            "node_id": "node-1",
            "node_created_at_utc": "2026-07-12T00:00:00Z",
            "host_name": "strategy-host",
        },
        "user": {
            "user_id": "user-1",
            "account_name": "analyst",
        },
        "session": {
            "session_id": "session-1",
            "session_started_at_utc": "2026-07-12T00:00:00Z",
        },
        "available_route_groups": ["workspace", "logs"],
        "package_mounts": [
            {
                "mount_id": "stratbox",
                "relative_path": "repositories/stratbox",
                "source_location_profile": "source_location_remote",
                "display_name": "Strategy Box Core",
                "source_ref": "https://github.com/ForestTiger-GH/stratbox.git",
            }
        ],
    }


def test_load_activation_context_reads_current_contract(tmp_path: Path) -> None:
    path = tmp_path / "activation.json"
    path.write_text(json.dumps(_payload(), ensure_ascii=False), encoding="utf-8")

    context = load_activation_context(path)

    assert context.world_id == "stratbox"
    assert context.active_surface_id == "desktop"
    assert context.workspace.primary_root.endswith("primary")
    assert context.workspace.package_root.endswith("appdock-packages")
    assert context.workspace.primary_source_location_profile == "source_location_remote"
    assert context.workspace.primary_content_runtime_profile == "content_runtime_managed_editable"
    assert context.package_mounts[0].mount_id == "stratbox"
    assert context.available_route_groups == ("workspace", "logs")


def test_load_activation_context_rejects_unsupported_major(tmp_path: Path) -> None:
    payload = _payload()
    payload["contract_version"] = "2.0"

    path = tmp_path / "activation.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(AppConfigError, match="Unsupported AppDock activation context contract version"):
        load_activation_context(path)


def test_load_activation_context_requires_current_workspace_fields(tmp_path: Path) -> None:
    payload = _payload()
    payload["workspace"].pop("package_root")

    path = tmp_path / "activation.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(AppConfigError, match="activation_context.workspace misses package_root"):
        load_activation_context(path)
