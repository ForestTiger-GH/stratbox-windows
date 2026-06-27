"""Рабочая схема бизнес-среды приложения."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from stratbox_windows.application.workspace.models import (
    WorkspaceSchema,
    DiagnosticItem,
    DiagnosticReport,
    DataRootStatus,
    WorkspaceRootStatus,
    WorkspaceResolution,
)
from stratbox_windows.application.workspace.explorer_models import (
    ExplorerEntry,
    ExplorerListing,
    ExplorerLocation,
    ExplorerSort,
)
from stratbox_windows.application.workspace.explorer_service import WorkspaceExplorerService
from stratbox_windows.application.workspace.registry import WorkspaceRegistry, load_workspace_registry
from stratbox_windows.application.workspace.diagnostics import resolve_data_root_status, run_workspace_diagnostics
from stratbox_windows.application.workspace.resolver import resolve_workspace_root

if TYPE_CHECKING:
    from stratbox.base.filestore import FileStore


def build_filestore_for_workspace_root(workspace_root_path: Path) -> 'FileStore':
    from stratbox_windows.application.workspace.filestore import build_filestore_for_workspace_root as _build_filestore_for_workspace_root

    return _build_filestore_for_workspace_root(workspace_root_path)


def build_filestore_for_data_root(data_root_path: Path) -> 'FileStore':
    from stratbox_windows.application.workspace.filestore import build_filestore_for_data_root as _build_filestore_for_data_root

    return _build_filestore_for_data_root(data_root_path)


__all__ = [
    "WorkspaceSchema",
    "DiagnosticItem",
    "DiagnosticReport",
    "DataRootStatus",
    "WorkspaceRootStatus",
    "WorkspaceResolution",
    "WorkspaceRegistry",
    "load_workspace_registry",
    "build_filestore_for_data_root",
    "build_filestore_for_workspace_root",
    "resolve_data_root_status",
    "resolve_workspace_root",
    "run_workspace_diagnostics",
    "ExplorerEntry",
    "ExplorerListing",
    "ExplorerLocation",
    "ExplorerSort",
    "WorkspaceExplorerService",
]
