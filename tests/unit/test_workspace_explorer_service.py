from __future__ import annotations

from pathlib import Path

from stratbox_windows.application.workspace import ExplorerSort, WorkspaceExplorerService


def test_workspace_explorer_service_lists_root_and_keeps_directories_first(tmp_path: Path) -> None:
    mount_root = tmp_path / 'mount'
    workspace_root = mount_root / 'Strategy Box Data'
    workspace_root.mkdir(parents=True)
    (workspace_root / 'input').mkdir()
    (workspace_root / 'output').mkdir()
    (workspace_root / 'report.xlsx').write_text('ok', encoding='utf-8')
    (workspace_root / 'data.csv').write_text('ok', encoding='utf-8')

    service = WorkspaceExplorerService(
        mount_root_path=mount_root,
        start_root_path=workspace_root,
        root_label='Strategy Box Data',
    )

    location = service.initial_location()
    assert location is not None

    listing = service.list_location(location, ExplorerSort(column='name', direction='asc'))

    assert listing.location.display_parts == ('Strategy Box Data',)
    assert [entry.name for entry in listing.entries[:2]] == ['input', 'output']
    assert listing.entries[2].type_label in {'CSV-файл', 'Лист Excel'}


def test_workspace_explorer_service_navigates_inside_workspace_only(tmp_path: Path) -> None:
    mount_root = tmp_path / 'mount'
    workspace_root = mount_root / 'Strategy Box Data'
    nested = workspace_root / 'input' / 'raw'
    nested.mkdir(parents=True)

    service = WorkspaceExplorerService(
        mount_root_path=mount_root,
        start_root_path=workspace_root,
        root_label='Strategy Box Data',
    )

    root = service.initial_location()
    assert root is not None
    listing = service.list_location(root, ExplorerSort())
    input_entry = next(entry for entry in listing.entries if entry.name == 'input')

    child = service.enter_entry(root, input_entry)
    assert child is not None
    assert child.display_parts == ('Strategy Box Data', 'input')
    assert child.can_go_up is True

    parent = service.parent_location(child)
    assert parent is not None
    assert parent.current_path == workspace_root
