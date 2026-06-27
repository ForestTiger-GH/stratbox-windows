from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ExplorerEntryKind = Literal['directory', 'file']
ExplorerSortColumn = Literal['name', 'type']
ExplorerSortDirection = Literal['asc', 'desc']


@dataclass(frozen=True, slots=True)
class ExplorerSort:
    column: ExplorerSortColumn = 'name'
    direction: ExplorerSortDirection = 'asc'

    def toggled(self, column: ExplorerSortColumn) -> 'ExplorerSort':
        if self.column == column:
            return ExplorerSort(column=column, direction='desc' if self.direction == 'asc' else 'asc')
        return ExplorerSort(column=column, direction='asc')


@dataclass(frozen=True, slots=True)
class ExplorerLocation:
    provider_id: str
    mount_root_path: Path
    start_root_path: Path
    current_path: Path
    root_label: str
    relative_parts: tuple[str, ...] = ()

    @property
    def is_root(self) -> bool:
        return self.current_path == self.start_root_path

    @property
    def can_go_up(self) -> bool:
        return not self.is_root

    @property
    def display_parts(self) -> tuple[str, ...]:
        return (self.root_label, *self.relative_parts)


@dataclass(frozen=True, slots=True)
class ExplorerEntry:
    entry_id: str
    name: str
    kind: ExplorerEntryKind
    path: Path
    relative_path: Path
    extension: str
    type_label: str
    icon_key: str
    is_navigable: bool
    is_openable: bool


@dataclass(frozen=True, slots=True)
class ExplorerListing:
    location: ExplorerLocation
    entries: tuple[ExplorerEntry, ...]
    sort: ExplorerSort
