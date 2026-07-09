from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _manifest() -> dict:
    return json.loads((ROOT / "appdock" / "manifest.json").read_text(encoding="utf-8"))


def _preset() -> dict:
    return json.loads((ROOT / "appdock" / "preset.json").read_text(encoding="utf-8"))


def test_manifest_and_preset_exist() -> None:
    manifest = ROOT / "appdock" / "manifest.json"
    preset = ROOT / "appdock" / "preset.json"

    assert manifest.is_file()
    assert preset.is_file()


def test_manifest_uses_stratbox_windows_entrypoint() -> None:
    activation = _manifest()["surfaces"][0]["activation"]

    assert activation["kind"] == "python_module"
    assert activation["target"] == "stratbox_windows.adapters.appdock.entry"


def test_manifest_is_local_only_surface() -> None:
    manifest = _manifest()
    surface = manifest["surfaces"][0]

    assert surface["compatible_modes"] == ["local"]
    assert manifest["profiles"]["supported_node_modes"] == ["local"]
    assert manifest["requirements"]["compatible_modes"] == ["local"]
    assert manifest["capabilities"]["supports_remote_attach"] is False
    assert manifest["capabilities"]["supports_delegated_jobs"] is False


def test_manifest_requests_install_root_system_dir() -> None:
    request = _manifest()["storage"]["requests"]["install_root_system_dir"]

    assert request["enabled"] is True
    assert request["directory_name"] == "stratbox-windows-system"


def test_preset_uses_system_install_and_force_update_profiles() -> None:
    preset = _preset()

    assert preset["platform_profile"] == "platform_windows"
    assert preset["output_format_profile"] == "output_format_exe"
    assert preset["install_profile"] == "install_local_system"
    assert preset["source_profile"] == "source_preset"
    assert preset["update_profile"] == "update_start_force"
    assert preset["node_profile"] == "node_disabled"
    assert preset["data_profile"] == "data_enabled"
    assert preset["data_location_profile"] == "data_location_local_preset"
    assert preset["welcome_profile"] == "welcome_banner"
    assert preset["entry_profile"] == "entry_direct"
    assert preset["brand_profile"] == "brand_disabled"


def test_preset_declares_manifest_bearing_primary_source() -> None:
    sources = _preset()["source_composition"]["sources"]
    manifest_sources = [item for item in sources if item["source_manifest_state"] == "source_manifest_included"]

    assert len(manifest_sources) == 1
    primary = manifest_sources[0]
    assert primary["source_ref"] == "https://github.com/ForestTiger-GH/stratbox-windows.git"
    assert primary["source_location_profile"] == "source_location_remote"
    assert primary["source_packaging_profile"] == "source_packaging_installable"
    assert primary["ref_kind"] == "branch"
    assert primary["ref"] == "main"


def test_preset_declares_secondary_stratbox_source() -> None:
    sources = _preset()["source_composition"]["sources"]
    secondary_sources = [item for item in sources if item["source_manifest_state"] == "source_manifest_none"]

    assert len(secondary_sources) == 1
    secondary = secondary_sources[0]
    assert secondary["mount_id"] == "stratbox"
    assert secondary["source_ref"] == "https://github.com/ForestTiger-GH/stratbox.git"
    assert secondary["source_location_profile"] == "source_location_remote"
    assert secondary["source_packaging_profile"] == "source_packaging_installable"
    assert secondary["installation_recipe"]["mode"] == "pip"
    assert secondary["installation_recipe"]["target"] == "."
    assert secondary["installation_recipe"]["editable"] is False
    assert secondary["installation_recipe"]["extras"] == []


def test_preset_feature_selection_matches_local_desktop_product() -> None:
    features = _preset()["feature_selection"]

    assert features["feature_update_enabled"] is True
    assert features["feature_node_enabled"] is False
    assert features["feature_data_enabled"] is True
    assert features["feature_brand_enabled"] is False


def test_preset_shortcuts_match_desktop_product_posture() -> None:
    shortcuts = _preset()["shortcut_policy"]

    assert shortcuts["desktop_shortcut"] is False
    assert shortcuts["start_menu_shortcut"] is True
    assert shortcuts["shortcut_target"] == "shell"


def test_preset_no_longer_uses_legacy_primary_and_package_blocks() -> None:
    preset = _preset()

    assert "primary_source" not in preset
    assert "package_composition" not in preset
    assert "update_policy" not in preset
    assert "visibility_policy" not in preset
    assert "first_run" not in preset
    assert "shell" not in preset
