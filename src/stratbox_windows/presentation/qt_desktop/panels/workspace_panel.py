from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMenu, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from stratbox_windows.application.workspace.explorer import build_workspace_explorer_sections
from stratbox_windows.presentation.qt_desktop.components.workspace_mount_header import WorkspaceMountHeader
from stratbox_windows.runtime.context import AppContext


class WorkspacePanel(QWidget):
    path_selected = Signal(str)
    open_path_requested = Signal(str)
    copy_path_requested = Signal(str)

    def __init__(self, context: AppContext, parent=None) -> None:
        super().__init__(parent)
        self._context = context
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 14, 18)
        layout.setSpacing(12)
        self._mount_header = WorkspaceMountHeader(self)
        layout.addWidget(self._mount_header)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setObjectName('workspaceTree')
        self.tree.itemDoubleClicked.connect(self._open_current)
        self.tree.itemSelectionChanged.connect(self._selection_changed)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_menu)
        layout.addWidget(self.tree, 1)
        self.refresh()

    def refresh(self) -> None:
        self._refresh_mount_header()
        self.tree.clear()
        sections = build_workspace_explorer_sections(self._context)
        if not sections:
            item = QTreeWidgetItem(['Workspace недоступен'])
            self.tree.addTopLevelItem(item)
            return
        for section in sections:
            root_item = QTreeWidgetItem([section.title])
            root_item.setData(0, Qt.UserRole, str(section.path))
            root_item.setToolTip(0, f'{section.description}\n{section.path}')
            self.tree.addTopLevelItem(root_item)
            if section.show_children:
                self._populate_children(root_item, section.path)
            root_item.setExpanded(section.id in {'workspace_root', 'input', 'output'})

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

    def _populate_children(self, item: QTreeWidgetItem, path: Path) -> None:
        if not path.exists() or not path.is_dir():
            missing = QTreeWidgetItem(['папка пока не создана'])
            missing.setData(0, Qt.UserRole, str(path))
            item.addChild(missing)
            return
        for nested in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))[:80]:
            nested_item = QTreeWidgetItem([nested.name])
            nested_item.setData(0, Qt.UserRole, str(nested))
            nested_item.setToolTip(0, str(nested))
            item.addChild(nested_item)

    def _current_path(self) -> str | None:
        item = self.tree.currentItem()
        if item is None:
            return None
        value = item.data(0, Qt.UserRole)
        return str(value) if value else None

    def _selection_changed(self) -> None:
        path = self._current_path()
        if path:
            self.path_selected.emit(path)

    def _open_current(self) -> None:
        path = self._current_path()
        if path:
            self.open_path_requested.emit(path)

    def _show_menu(self, pos) -> None:
        path = self._current_path()
        if not path:
            return
        menu = QMenu(self)
        open_action = menu.addAction('Открыть')
        copy_action = menu.addAction('Скопировать путь')
        refresh_action = menu.addAction('Обновить')
        selected = menu.exec(self.tree.mapToGlobal(pos))
        if selected == open_action:
            self.open_path_requested.emit(path)
        elif selected == copy_action:
            self.copy_path_requested.emit(path)
        elif selected == refresh_action:
            self.refresh()
