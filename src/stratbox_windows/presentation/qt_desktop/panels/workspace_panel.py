from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QMenu,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from stratbox_windows.application.workspace import ExplorerEntry, ExplorerSort, WorkspaceExplorerService
from stratbox_windows.presentation.qt_desktop.components.workspace_mount_header import WorkspaceMountHeader
from stratbox_windows.presentation.qt_desktop.components.workspace_path_bar import WorkspacePathBar
from stratbox_windows.presentation.qt_desktop.workspace.explorer_table_model import ExplorerTableModel
from stratbox_windows.runtime.context import AppContext


class WorkspacePanel(QWidget):
    path_selected = Signal(str)
    open_path_requested = Signal(str)
    copy_path_requested = Signal(str)

    def __init__(self, context: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName('leftPanelSection')
        self._context = context
        self._service: WorkspaceExplorerService | None = None
        self._location = None
        self._sort = ExplorerSort(column='name', direction='asc')
        self._icons = self._load_icons()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 14, 18)
        layout.setSpacing(10)

        self._mount_header = WorkspaceMountHeader(self)
        layout.addWidget(self._mount_header)

        self._path_bar = WorkspacePathBar(self)
        self._path_bar.up_requested.connect(self._navigate_up)
        layout.addWidget(self._path_bar)

        self._empty_label = QLabel(self)
        self._empty_label.setObjectName('workspaceExplorerPlaceholder')
        self._empty_label.setWordWrap(True)
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.hide()
        layout.addWidget(self._empty_label)

        self._table_model = ExplorerTableModel(self)
        self._table_model.set_icons(self._icons)

        self.table = QTableView(self)
        self.table.setObjectName('workspaceExplorerTable')
        self.table.setModel(self._table_model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setSortingEnabled(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.doubleClicked.connect(self._activate_current)
        self.table.customContextMenuRequested.connect(self._show_menu)
        self.table.selectionModel().selectionChanged.connect(lambda *_: self._selection_changed())
        header = self.table.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self._toggle_sort)
        header.setSortIndicatorShown(True)
        header.setHighlightSections(False)
        header.setSectionResizeMode(ExplorerTableModel.NAME_COLUMN, QHeaderView.Stretch)
        header.setSectionResizeMode(ExplorerTableModel.TYPE_COLUMN, QHeaderView.ResizeToContents)
        self.table.verticalHeader().hide()
        self.table.setWordWrap(False)
        layout.addWidget(self.table, 1)

        self.refresh()

    def refresh(self) -> None:
        self._refresh_mount_header()
        self._service = self._build_service()
        previous_path = self._location.current_path if self._location is not None else None
        self._location = self._service.location_for_path(previous_path) if self._service else None
        if self._location is None and self._service is not None:
            self._location = self._service.initial_location()
        self._render_location()

    def _build_service(self) -> WorkspaceExplorerService:
        mount_root = self._preferred_mount_path()
        workspace_root = self._context.workspace_root_path
        root_label = workspace_root.name if workspace_root is not None else self._context.workspace_schema.workspace_dirname
        return WorkspaceExplorerService(
            mount_root_path=mount_root,
            start_root_path=workspace_root,
            root_label=root_label,
        )

    def _refresh_mount_header(self) -> None:
        data_root_path = self._preferred_mount_path()
        display_text = f'({str(data_root_path)})' if data_root_path else '(недоступно)'
        status_text = self._context.data_root_status.message
        self._mount_header.set_mount(
            path_text=display_text,
            available=bool(self._context.data_root_status.available and data_root_path is not None),
            status_text=status_text,
        )

    def _preferred_mount_path(self) -> Path | None:
        return (
            self._context.data_root_status.path
            or self._context.data_root_selector_path
            or self._context.workspace_root_path
        )

    def _render_location(self) -> None:
        if self._service is None or self._location is None:
            self._table_model.set_listing(None)
            self.table.clearSelection()
            self.table.setVisible(False)
            self._path_bar.set_path(parts=('Рабочая область',), can_go_up=False, tooltip_text='')
            self._empty_label.setText(self._context.workspace_status.message or 'Рабочая область Strategy Box пока недоступна.')
            self._empty_label.show()
            return
        listing = self._service.list_location(self._location, self._sort)
        self._table_model.set_listing(listing)
        self.table.setVisible(True)
        self._empty_label.hide()
        self._path_bar.set_path(
            parts=listing.location.display_parts,
            can_go_up=listing.location.can_go_up,
            tooltip_text=str(listing.location.current_path),
        )
        self.table.horizontalHeader().setSortIndicator(
            ExplorerTableModel.NAME_COLUMN if self._sort.column == 'name' else ExplorerTableModel.TYPE_COLUMN,
            Qt.AscendingOrder if self._sort.direction == 'asc' else Qt.DescendingOrder,
        )
        if listing.entries:
            self.table.selectRow(0)
        else:
            self.table.clearSelection()

    def _current_entry(self) -> ExplorerEntry | None:
        index = self.table.currentIndex()
        if not index.isValid():
            return None
        return self._table_model.entry_by_row(index.row())

    def _selection_changed(self) -> None:
        entry = self._current_entry()
        if entry is not None:
            self.path_selected.emit(str(entry.path))

    def _activate_current(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        if entry.is_navigable:
            self._enter_entry(entry)
            return
        if entry.is_openable:
            self.open_path_requested.emit(str(entry.path))

    def _enter_entry(self, entry: ExplorerEntry) -> None:
        if self._service is None or self._location is None:
            return
        target = self._service.enter_entry(self._location, entry)
        if target is None:
            return
        self._location = target
        self._render_location()

    def _navigate_up(self) -> None:
        if self._service is None or self._location is None:
            return
        target = self._service.parent_location(self._location)
        if target is None:
            return
        self._location = target
        self._render_location()

    def _toggle_sort(self, section: int) -> None:
        column = 'name' if section == ExplorerTableModel.NAME_COLUMN else 'type'
        self._sort = self._sort.toggled(column)  # type: ignore[arg-type]
        self._render_location()

    def _show_menu(self, pos) -> None:
        index = self.table.indexAt(pos)
        if index.isValid():
            self.table.setCurrentIndex(index)
        else:
            self.table.clearSelection()
        entry = self._current_entry()
        menu = QMenu(self)
        refresh_action = menu.addAction('Обновить')
        open_action = None
        copy_action = None
        up_action = None
        if entry is not None:
            open_action = menu.addAction('Открыть' if not entry.is_navigable else 'Открыть папку')
            copy_action = menu.addAction('Скопировать путь')
        if self._location is not None and self._location.can_go_up:
            up_action = menu.addAction('Вверх')
        chosen = menu.exec(self.table.viewport().mapToGlobal(pos))
        if chosen == refresh_action:
            self.refresh()
        elif chosen == open_action and entry is not None:
            if entry.is_navigable:
                self._enter_entry(entry)
            else:
                self.open_path_requested.emit(str(entry.path))
        elif chosen == copy_action and entry is not None:
            self.copy_path_requested.emit(str(entry.path))
        elif chosen == up_action:
            self._navigate_up()

    @staticmethod
    def _load_icons() -> dict[str, QIcon]:
        icons_root = Path(__file__).resolve().parents[3] / 'resources' / 'icons' / 'files'
        icon_map: dict[str, QIcon] = {}
        for name in ('folder', 'file', 'excel', 'csv', 'json', 'text', 'pdf', 'image', 'archive'):
            path = icons_root / f'{name}.svg'
            if path.exists():
                icon_map[name] = QIcon(str(path))
        return icon_map
