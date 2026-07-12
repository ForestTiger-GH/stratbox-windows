from __future__ import annotations

from pathlib import Path

from stratbox_windows.adapters.appdock.runtime_contracts import AppActivationContext
from stratbox_windows.runtime.paths import build_app_paths


def test_build_app_paths_standalone_dev_creates_expected_layout(tmp_path: Path) -> None:
    paths = build_app_paths(standalone_dev_root=tmp_path)

    assert paths.storage_mode == "standalone_dev_root"
    assert paths.dev_root == tmp_path
    assert paths.product_root == Path(__file__).resolve().parents[2]
    assert paths.app_storage_root == tmp_path / ".stratbox_windows" / "system"
    assert paths.logs_dir.exists()
    assert paths.operation_logs_dir.exists()
    assert paths.runtime_dir.exists()
    assert paths.app_config_path.name == "app.json"


def test_build_app_paths_reads_appdock_primary_root(tmp_path: Path) -> None:
    activation = AppActivationContext.from_dict(
        {
            "contract_version": "1.0",
            "generated_at_utc": "2026-06-27T00:00:00Z",
            "world": {"world_id": "stratbox", "display_name": "Strategy Box"},
            "active_surface": {"surface_id": "desktop", "entry_view": "scenario_chat"},
            "source_revision": {"ref_kind": "branch", "ref": "main"},
            "workspace": {
                "install_root": str(tmp_path / "install"),
                "system_root": str(tmp_path / "install" / "appdock-system"),
                "package_root": str(tmp_path / "packages"),
                "data_root_status": "configured",
                "primary_root": str(tmp_path / "packages" / "repositories" / "primary"),
                "primary_source_location_profile": "source_location_remote",
                "primary_content_runtime_profile": "content_runtime_managed_editable",
            },
            "refs": {},
        }
    )

    paths = build_app_paths(appdock_activation=activation)

    assert paths.storage_mode == "appdock_managed"
    assert paths.product_root == tmp_path / "packages" / "repositories" / "primary"
    assert paths.src_dir == tmp_path / "packages" / "repositories" / "primary" / "src"
    assert paths.package_root == tmp_path / "packages"
    assert paths.app_storage_root == tmp_path / "install" / "appdock-system"
    assert paths.managed_system_root == tmp_path / "install" / "appdock-system"
