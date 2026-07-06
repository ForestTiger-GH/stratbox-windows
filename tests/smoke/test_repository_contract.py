from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_manifest_and_preset_exist() -> None:
    manifest = ROOT / "appdock" / "manifest.json"
    preset = ROOT / "appdock" / "preset.json"

    assert manifest.is_file()
    assert preset.is_file()


def test_manifest_uses_stratbox_windows_entrypoint() -> None:
    manifest = json.loads((ROOT / "appdock" / "manifest.json").read_text(encoding="utf-8"))
    activation = manifest["surfaces"][0]["activation"]

    assert activation["kind"] == "python_module"
    assert activation["target"] == "stratbox_windows.adapters.appdock.entry"


def test_manifest_is_local_only_surface() -> None:
    manifest = json.loads((ROOT / "appdock" / "manifest.json").read_text(encoding="utf-8"))
    surface = manifest["surfaces"][0]

    assert surface["compatible_modes"] == ["local"]
    assert manifest["profiles"]["supported_node_modes"] == ["local"]
    assert manifest["requirements"]["compatible_modes"] == ["local"]
    assert manifest["capabilities"]["supports_remote_attach"] is False
    assert manifest["capabilities"]["supports_delegated_jobs"] is False


def test_preset_uses_locked_runtime_snapshot_from_github_main() -> None:
    preset = json.loads((ROOT / "appdock" / "preset.json").read_text(encoding="utf-8"))
    primary = preset["primary_source"]

    assert primary["source_form"] == "runtime_snapshot"
    assert primary["entry_mode"] == "preset_locked"
    assert primary["fixed_locator"] == "https://github.com/ForestTiger-GH/stratbox-windows.git"
    assert primary["ref_kind"] == "branch"
    assert primary["ref"] == "main"
    assert primary["refresh_policy"] == "on_launch"
    assert primary["refresh_failure_policy"] == "use_local"
    assert primary["modified_checkout_policy"] == "recreate"


def test_preset_declares_additional_stratbox_package_source() -> None:
    preset = json.loads((ROOT / "appdock" / "preset.json").read_text(encoding="utf-8"))
    sources = preset["package_composition"]["package_sources"]

    assert sources
    assert sources[0]["mount_id"] == "stratbox"
    assert sources[0]["include_mode"] == "packaged_snapshot"
    assert sources[0]["probe_policy"] == "skip_source_probe"
    assert sources[0]["installation_recipe"]["mode"] == "pip"
    assert sources[0]["installation_recipe"]["editable"] is False


def test_preset_uses_machine_managed_system_install() -> None:
    preset = json.loads((ROOT / "appdock" / "preset.json").read_text(encoding="utf-8"))
    install = preset["install_context"]

    assert install["mode"] == "machine_managed_install"
    assert install["allow_install_root_override"] is False
    assert install["package_root_policy"] == "platform_managed"
    assert install["data_root_policy"] == "platform_managed"


def test_preset_opens_strategy_box_after_setup() -> None:
    preset = json.loads((ROOT / "appdock" / "preset.json").read_text(encoding="utf-8"))

    assert preset["shell"]["post_setup_entry"]["profile_id"] == "direct_entry_surface"
    assert preset["first_run"]["open_shell_after_first_setup"] is False


def test_preset_refreshes_primary_and_package_sources_on_launch() -> None:
    preset = json.loads((ROOT / "appdock" / "preset.json").read_text(encoding="utf-8"))
    update = preset["update_policy"]

    assert update["source_refresh"] == "on_launch"
    assert update["package_refresh"] == "on_launch"
    assert update["release_update"] == "manual"


def test_preset_hides_locked_source_step() -> None:
    preset = json.loads((ROOT / "appdock" / "preset.json").read_text(encoding="utf-8"))
    visibility = preset["visibility_policy"]

    assert visibility["show_source_step"] is False
    assert visibility["show_preview_step"] is False
    assert visibility["show_install_step"] is True
    assert visibility["show_review_step"] is True
