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


def test_preset_hides_source_step_for_locked_product_mode() -> None:
    preset = json.loads((ROOT / "appdock" / "preset.json").read_text(encoding="utf-8"))
    visibility = preset["visibility_policy"]

    assert visibility["show_source_step"] is False
    assert visibility["show_preview_step"] is True
    assert visibility["show_install_step"] is True
    assert visibility["show_review_step"] is True


def test_preset_declares_bundled_stratbox_core_dependency() -> None:
    preset = json.loads((ROOT / "appdock" / "preset.json").read_text(encoding="utf-8"))
    aux = preset["bundle_composition"]["auxiliary_sources"]

    assert aux
    assert aux[0]["mount_id"] == "stratbox-core"
    assert aux[0]["runtime_install_mode"] == "pip"
    assert aux[0]["runtime_install_editable"] is False
