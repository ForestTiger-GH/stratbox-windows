from __future__ import annotations

import json
from pathlib import Path

import pytest

from stratbox_windows.adapters.appdock.runtime_contracts import load_activation_context
from stratbox_windows.runtime.errors import AppConfigError


def _payload() -> dict:
    return {
        "contract_version": "1.0",
        "generated_at_utc": "2026-06-24T00:00:00Z",
        "world": {
            "world_id": "stratbox-windows",
            "display_name": "Strategy Box",
        },
        "active_surface": {
            "surface_id": "stratbox_windows.desktop",
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
            "system_root": "C:/StrategyBox/stratbox-windows-system",
            "source_root": "C:/StrategyBox/appdock-bundles/repositories/primary",
            "bundle_root": "C:/StrategyBox/appdock-bundles",
            "data_root_status": "available",
            "data_root_path": "D:/BusinessData",
        },
        "provided_system_dirs": {
            "install_root_system_dir": {
                "kind": "install_root_system_dir",
                "directory_name": "stratbox-windows-system",
                "path": "C:/StrategyBox/stratbox-windows-system",
                "provider_class": "install_root",
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
            "node_created_at_utc": "2026-06-24T00:00:00Z",
            "host_name": "strategy-host",
        },
        "user": {
            "user_id": "user-1",
            "account_name": "analyst",
        },
        "session": {
            "session_id": "session-1",
            "session_started_at_utc": "2026-06-24T00:00:00Z",
        },
        "available_route_groups": ["workspace", "logs"],
    }


def test_load_activation_context_reads_supported_contract(tmp_path: Path) -> None:
    path = tmp_path / "activation.json"
    path.write_text(json.dumps(_payload(), ensure_ascii=False), encoding="utf-8")

    context = load_activation_context(path)

    assert context.world_id == "stratbox-windows"
    assert context.active_surface_id == "stratbox_windows.desktop"
    assert context.workspace.source_root.endswith("primary")
    assert context.available_route_groups == ("workspace", "logs")


def test_load_activation_context_rejects_unsupported_major(tmp_path: Path) -> None:
    payload = _payload()
    payload["contract_version"] = "2.0"

    path = tmp_path / "activation.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(AppConfigError, match="Unsupported AppDock activation context contract version"):
        load_activation_context(path)
