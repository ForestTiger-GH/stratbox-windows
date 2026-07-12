from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _manifest() -> dict:
    return json.loads((ROOT / "appdock" / "manifest.json").read_text(encoding="utf-8"))


def test_repository_uses_single_connector_manifest() -> None:
    assert (ROOT / "appdock" / "manifest.json").is_file()
    assert not (ROOT / "appdock" / "preset.json").exists()


def test_manifest_declares_minimal_strategy_box_world() -> None:
    manifest = _manifest()

    assert manifest["contract_version"] == "1.0"
    assert manifest["identity"] == {
        "world_id": "stratbox",
        "world_name": "Strategy Box",
    }
    assert manifest["default_surface_id"] == "desktop"
    assert set(manifest) == {
        "contract_version",
        "identity",
        "world_definition",
        "default_surface_id",
        "surfaces",
    }


def test_manifest_enables_data_without_preselecting_binding() -> None:
    definition = _manifest()["world_definition"]

    assert definition["data_profile"] == "data_enabled"
    assert "data_location_profile" not in definition
    assert "data_binding_profile" not in definition
    assert "data_locator" not in definition


def test_manifest_declares_desktop_entrypoint() -> None:
    surface = _manifest()["surfaces"][0]
    activation = surface["activation"]

    assert surface["surface_id"] == "desktop"
    assert activation["kind"] == "python_module"
    assert activation["target"] == "stratbox_windows.adapters.appdock.entry"
    assert activation["diagnostics"] == {
        "strategy": "flag",
        "flag": "--diagnose",
        "timeout_seconds": 30,
    }


def test_manifest_declares_external_stratbox_core_source() -> None:
    sources = _manifest()["world_definition"]["sources"]

    assert sources == [
        {
            "source_ref": "https://github.com/ForestTiger-GH/stratbox.git",
            "source_location_profile": "source_location_remote",
            "source_packaging_profile": "source_packaging_installable",
            "display_name": "Strategy Box Core",
            "mount_id": "stratbox",
        }
    ]
