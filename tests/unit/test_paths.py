from __future__ import annotations

from pathlib import Path

from stratbox_windows.runtime.paths import build_app_paths


def test_build_app_paths_standalone_dev_creates_expected_layout(tmp_path: Path) -> None:
    paths = build_app_paths(standalone_dev_root=tmp_path)

    assert paths.storage_mode == "standalone_dev_root"
    assert paths.dev_root == tmp_path
    assert paths.app_storage_root == tmp_path / ".stratbox_windows" / "system"
    assert paths.logs_dir.exists()
    assert paths.operation_logs_dir.exists()
    assert paths.runtime_dir.exists()
    assert paths.app_config_path.name == "app.json"
