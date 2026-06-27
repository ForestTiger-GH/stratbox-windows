from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QIcon

from stratbox_windows.application.workspace.explorer_models import ExplorerEntry, ExplorerListing


class ExplorerTableModel(QAbstractTableModel):
    NAME_COLUMN = 0
    TYPE_COLUMN = 1

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._listing: ExplorerListing | None = None
        self._icons: dict[str, QIcon] = {}

    def set_listing(self, listing: ExplorerListing | None) -> None:
        self.beginResetModel()
        self._listing = listing
        self.endResetModel()

    def set_icons(self, icons: dict[str, QIcon]) -> None:
        self._icons = icons
        if self.rowCount() > 0:
            top_left = self.index(0, 0)
            bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid() or self._listing is None:
            return 0
        return len(self._listing.entries)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else 2

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        entry = self.entry_at(index)
        if entry is None:
            return None
        if role == Qt.DisplayRole:
            if index.column() == self.NAME_COLUMN:
                return entry.name
            if index.column() == self.TYPE_COLUMN:
                return entry.type_label
        if role == Qt.DecorationRole and index.column() == self.NAME_COLUMN:
            return self._icons.get(entry.icon_key) or self._icons.get('file')
        if role == Qt.ToolTipRole:
            return str(entry.path)
        if role == Qt.UserRole:
            return str(entry.path)
        if role == Qt.UserRole + 1:
            return entry.kind
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):  # noqa: N802
        if orientation != Qt.Horizontal or role != Qt.DisplayRole:
            return None
        if section == self.NAME_COLUMN:
            return 'Имя'
        if section == self.TYPE_COLUMN:
            return 'Тип'
        return None

    def entry_at(self, index: QModelIndex) -> ExplorerEntry | None:
        if not index.isValid() or self._listing is None:
            return None
        if not (0 <= index.row() < len(self._listing.entries)):
            return None
        return self._listing.entries[index.row()]

    def entry_by_row(self, row: int) -> ExplorerEntry | None:
        if self._listing is None or not (0 <= row < len(self._listing.entries)):
            return None
        return self._listing.entries[row]

    def listing(self) -> ExplorerListing | None:
        return self._listing
