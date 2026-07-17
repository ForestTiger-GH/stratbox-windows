from __future__ import annotations

from pathlib import Path

from stratbox_windows.adapters.appdock.runtime_contracts import AppActivationContext
from stratbox_windows.runtime.paths import build_app_paths


def test_build_app_paths_standalone_dev_creates_expected_layout(tmp_path: Path) -> None:
    paths = build_app_paths(standalone_dev_root=tmp_path)

    assert paths.storage_mode == 'standalone_dev_root'
    assert paths.dev_root == tmp_path
    assert paths.product_root == Path(__file__).resolve().parents[2]
    assert paths.app_storage_root == tmp_path / '.stratbox_windows' / 'system'
    assert paths.logs_dir.exists()
    assert paths.operation_logs_dir.exists()
    assert paths.runtime_dir.exists()
    assert paths.app_config_path.name == 'app.json'


def test_build_app_paths_reads_appdock_source_root(
    tmp_path: Path,
    appdock_activation_payload: dict,
) -> None:
    activation = AppActivationContext.from_dict(appdock_activation_payload)

    paths = build_app_paths(appdock_activation=activation)

    source_root = Path(appdock_activation_payload['workspace']['source_root'])
    system_root = Path(appdock_activation_payload['provided_system_dirs']['install_root_system_dir']['path'])
    assert paths.storage_mode == 'appdock_managed'
    assert paths.product_root == source_root
    assert paths.src_dir == source_root / 'src'
    assert paths.package_root == Path(appdock_activation_payload['workspace']['package_root'])
    assert paths.app_storage_root == system_root
    assert paths.managed_system_root == system_root
    assert paths.runtime_state_path == Path(appdock_activation_payload['refs']['runtime_state_ref'])
