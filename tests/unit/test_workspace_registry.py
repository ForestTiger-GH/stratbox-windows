from __future__ import annotations

from stratbox_windows.application.workspace.registry import load_workspace_registry


def test_workspace_registry_loads_default_schema() -> None:
    registry = load_workspace_registry()

    assert registry.items
    assert registry.has("default")

    schema = registry.get("default")
    assert schema.title == "Standard workspace"
    assert "input" in schema.required_dirs
    assert "output" in schema.required_dirs
