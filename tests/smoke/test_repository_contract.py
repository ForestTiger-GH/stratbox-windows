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


def test_preset_declares_bundled_stratbox_core_dependency() -> None:
    preset = json.loads((ROOT / "appdock" / "preset.json").read_text(encoding="utf-8"))
    aux = preset["bundle_composition"]["auxiliary_sources"]

    assert aux
    assert aux[0]["mount_id"] == "stratbox-core"
    assert aux[0]["runtime_install_mode"] == "pip"
