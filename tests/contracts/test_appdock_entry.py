from __future__ import annotations

import json
import sys
from pathlib import Path

from stratbox_windows.adapters.appdock.entry import _activate_stratbox_package_mount


def test_entry_activates_declared_stratbox_package_mount(tmp_path: Path, monkeypatch) -> None:
    package_root = tmp_path / "packages"
    mounted_src = package_root / "repositories" / "stratbox" / "src"
    (mounted_src / "stratbox").mkdir(parents=True)

    activation_path = tmp_path / "activation.json"
    activation_path.write_text(
        json.dumps(
            {
                "contract_version": "1.0",
                "generated_at_utc": "2026-07-12T00:00:00Z",
                "world": {"world_id": "stratbox"},
                "active_surface": {"surface_id": "desktop"},
                "source_revision": {"ref_kind": "branch", "ref": "main"},
                "workspace": {
                    "install_root": str(tmp_path / "install"),
                    "system_root": str(tmp_path / "install" / "system"),
                    "package_root": str(package_root),
                    "data_root_status": "configured",
                    "primary_root": str(tmp_path / "primary"),
                    "primary_source_location_profile": "source_location_remote",
                    "primary_content_runtime_profile": "content_runtime_managed_editable",
                },
                "refs": {},
                "package_mounts": [
                    {
                        "mount_id": "stratbox",
                        "relative_path": "repositories/stratbox",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("APPDOCK_ACTIVATION_CONTEXT_PATH", str(activation_path))

    original = list(sys.path)
    try:
        _activate_stratbox_package_mount()
        assert sys.path[0] == str(mounted_src)
    finally:
        sys.path[:] = original
