from __future__ import annotations

from pathlib import Path

from stratbox_windows.application.workspace.explorer_models import (
    ExplorerEntry,
    ExplorerListing,
    ExplorerLocation,
    ExplorerSort,
)
from stratbox_windows.application.workspace.explorer_provider import ExplorerProvider, LocalWorkspaceExplorerProvider
from stratbox_windows.application.workspace.file_types import resolve_file_type


class WorkspaceExplorerService:
    def __init__(
        self,
        *,
        mount_root_path: Path | None,
        start_root_path: Path | None,
        root_label: str,
        provider: ExplorerProvider | None = None,
    ) -> None:
        self._mount_root_path = mount_root_path
        self._start_root_path = start_root_path
        self._root_label = root_label
        self._provider = provider or LocalWorkspaceExplorerProvider()

    @property
    def available(self) -> bool:
        return self._mount_root_path is not None and self._start_root_path is not None and self._provider.exists(self._start_root_path)

    def initial_location(self) -> ExplorerLocation | None:
        return self.location_for_path(self._start_root_path)

    def location_for_path(self, path: Path | None) -> ExplorerLocation | None:
        if not self.available or path is None:
            return None
        assert self._mount_root_path is not None
        assert self._start_root_path is not None
        try:
            resolved = path if path.is_absolute() else self._start_root_path / path
            resolved = resolved.resolve()
            start_root = self._start_root_path.resolve()
        except Exception:
            return None
        if resolved != start_root:
            try:
                resolved.relative_to(start_root)
            except ValueError:
                return None
        if not self._provider.exists(resolved) or not self._provider.is_dir(resolved):
            return None
        relative = resolved.relative_to(self._start_root_path) if resolved != self._start_root_path else Path('.')
        return ExplorerLocation(
            provider_id=self._provider.provider_id,
            mount_root_path=self._mount_root_path,
            start_root_path=self._start_root_path,
            current_path=resolved,
            root_label=self._root_label,
            relative_parts=tuple() if str(relative) == '.' else tuple(relative.parts),
        )

    def parent_location(self, location: ExplorerLocation) -> ExplorerLocation | None:
        if not location.can_go_up:
            return None
        parent = location.current_path.parent
        relative = parent.relative_to(location.start_root_path) if parent != location.start_root_path else Path('.')
        return ExplorerLocation(
            provider_id=location.provider_id,
            mount_root_path=location.mount_root_path,
            start_root_path=location.start_root_path,
            current_path=parent,
            root_label=location.root_label,
            relative_parts=tuple() if str(relative) == '.' else tuple(relative.parts),
        )

    def enter_entry(self, location: ExplorerLocation, entry: ExplorerEntry) -> ExplorerLocation | None:
        if not entry.is_navigable:
            return None
        target = entry.path
        if not self._provider.exists(target) or not self._provider.is_dir(target):
            return None
        relative = target.relative_to(location.start_root_path) if target != location.start_root_path else Path('.')
        return ExplorerLocation(
            provider_id=location.provider_id,
            mount_root_path=location.mount_root_path,
            start_root_path=location.start_root_path,
            current_path=target,
            root_label=location.root_label,
            relative_parts=tuple() if str(relative) == '.' else tuple(relative.parts),
        )

    def list_location(self, location: ExplorerLocation, sort: ExplorerSort) -> ExplorerListing:
        raw_children = self._provider.list_children(location.current_path)
        entries = [self._build_entry(location, child) for child in raw_children]
        entries.sort(key=lambda entry: self._sort_key(entry, sort), reverse=(sort.direction == 'desc'))
        if location.can_go_up:
            parent = location.current_path.parent
            entries.insert(0, self._build_navigation_up_entry(location, parent))
        return ExplorerListing(location=location, entries=tuple(entries), sort=sort)

    def _build_entry(self, location: ExplorerLocation, child: Path) -> ExplorerEntry:
        is_directory = self._provider.is_dir(child)
        kind = 'directory' if is_directory else 'file'
        if is_directory:
            type_label = 'Папка'
            icon_key = 'folder'
            extension = ''
        else:
            icon_key, type_label = resolve_file_type(child)
            extension = child.suffix.lower()
        relative_path = child.relative_to(location.start_root_path)
        return ExplorerEntry(
            entry_id=str(relative_path),
            name=child.name,
            kind=kind,
            path=child,
            relative_path=relative_path,
            extension=extension,
            type_label=type_label,
            icon_key=icon_key,
            is_navigable=is_directory,
            is_openable=True,
        )

    def _build_navigation_up_entry(self, location: ExplorerLocation, target: Path) -> ExplorerEntry:
        return ExplorerEntry(
            entry_id='..',
            name='↖ Вверх',
            kind='navigate_up',
            path=target,
            relative_path=Path('..'),
            extension='',
            type_label='Папка',
            icon_key='folder',
            is_navigable=False,
            is_openable=False,
        )

    @staticmethod
    def _sort_key(entry: ExplorerEntry, sort: ExplorerSort) -> tuple:
        bucket = 0 if entry.kind == 'directory' else 1
        if sort.column == 'type':
            return (bucket, entry.type_label.lower(), entry.name.lower())
        return (bucket, entry.name.lower(), entry.type_label.lower())
