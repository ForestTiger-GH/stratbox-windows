from __future__ import annotations

from pathlib import Path

from stratbox_windows.application.workspace.models import WorkspaceSchema
from stratbox_windows.application.workspace.resolver import resolve_workspace_root


def test_workspace_resolver_creates_workspace_below_selector(tmp_path: Path) -> None:
    selector = tmp_path / "BusinessRoot"
    selector.mkdir()

    schema = WorkspaceSchema(
        id="default",
        title="Default",
        required_dirs=("input", "output"),
        auto_create_workspace_root=True,
        auto_create_required_dirs=True,
    )

    resolution = resolve_workspace_root(
        schema,
        selector,
        run_mode="standalone_dev",
        create_missing=True,
    )

    assert resolution.workspace_root_path is not None
    assert resolution.workspace_root_path.exists()
    assert (resolution.workspace_root_path / "input").exists()
    assert (resolution.workspace_root_path / "output").exists()
