"""Strict AppDock Activation Context 3.0 adapter for Strategy Box Windows.

The module intentionally stays stdlib-only.  It mirrors the public AppDock
runtime handoff without importing AppDock internals into the product runtime.
Unknown fields, old contract versions and malformed runtime package projections
are rejected at the boundary.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

from stratbox_windows.runtime.errors import AppConfigError

ACTIVATION_CONTEXT_CONTRACT_VERSION = '3.0'
ACTIVATION_CONTEXT_ENV = 'APPDOCK_ACTIVATION_CONTEXT_PATH'
APPDOCK_CONFIG_ENV = 'APPDOCK_CONFIG_PATH'


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AppConfigError(f'{field} must be an object')
    return value


def _reject_unknown(payload: Mapping[str, Any], allowed: set[str], field: str) -> None:
    unknown = set(payload) - allowed
    if unknown:
        raise AppConfigError(f'{field} contains unsupported fields: {", ".join(sorted(unknown))}')


def _required_string(payload: Mapping[str, Any], key: str, *, scope: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AppConfigError(f'{scope} misses {key}')
    return value.strip()


def _optional_string(value: Any, *, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise AppConfigError(f'{field} must be a string or null')
    normalized = value.strip()
    return normalized or None


def _optional_mapping(value: Any, *, field: str) -> Mapping[str, Any] | None:
    if value in (None, {}):
        return None
    return _mapping(value, field)


def _required_bool(value: Any, *, field: str) -> bool:
    if type(value) is not bool:
        raise AppConfigError(f'{field} must be a boolean')
    return value


def _string_tuple(value: Any, *, field: str) -> tuple[str, ...]:
    if value is None:
        return tuple()
    if not isinstance(value, (list, tuple)):
        raise AppConfigError(f'{field} must be an array')
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise AppConfigError(f'{field}[{index}] must be a non-empty string')
        result.append(item.strip())
    if len(set(result)) != len(result):
        raise AppConfigError(f'{field} must contain unique values')
    return tuple(result)


def _sha256(value: Any, *, field: str) -> str:
    if not isinstance(value, str):
        raise AppConfigError(f'{field} must be a SHA-256 digest')
    digest = value.strip().lower()
    if len(digest) != 64 or any(char not in '0123456789abcdef' for char in digest):
        raise AppConfigError(f'{field} must be a SHA-256 digest')
    return digest


def _contract_version(value: Any) -> str:
    if value != ACTIVATION_CONTEXT_CONTRACT_VERSION:
        raise AppConfigError(
            f'Unsupported AppDock activation context contract version: {value!r}. '
            f'Strategy Box requires {ACTIVATION_CONTEXT_CONTRACT_VERSION}.'
        )
    return ACTIVATION_CONTEXT_CONTRACT_VERSION


@dataclass(frozen=True, slots=True)
class SourceRevisionRef:
    ref_kind: str
    ref: str
    commit: str | None = None
    sync_mode: str | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> 'SourceRevisionRef':
        raw = _mapping(payload, 'activation_context.source_revision')
        _reject_unknown(raw, {'ref_kind', 'ref', 'commit', 'sync_mode'}, 'activation_context.source_revision')
        return cls(
            ref_kind=_required_string(raw, 'ref_kind', scope='activation_context.source_revision'),
            ref=_required_string(raw, 'ref', scope='activation_context.source_revision'),
            commit=_optional_string(raw.get('commit'), field='activation_context.source_revision.commit'),
            sync_mode=_optional_string(raw.get('sync_mode'), field='activation_context.source_revision.sync_mode'),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActivationWorkspace:
    install_root: str
    user_workspace_root: str
    system_root: str
    source_root: str
    package_root: str
    data_root_status: str
    data_root_path: str | None = None
    source_location_profile: str | None = None
    content_runtime_profile: str | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> 'ActivationWorkspace':
        raw = _mapping(payload, 'activation_context.workspace')
        _reject_unknown(
            raw,
            {
                'install_root', 'user_workspace_root', 'system_root', 'source_root', 'package_root',
                'data_root_status', 'data_root_path', 'source_location_profile', 'content_runtime_profile',
            },
            'activation_context.workspace',
        )
        return cls(
            install_root=_required_string(raw, 'install_root', scope='activation_context.workspace'),
            user_workspace_root=_required_string(raw, 'user_workspace_root', scope='activation_context.workspace'),
            system_root=_required_string(raw, 'system_root', scope='activation_context.workspace'),
            source_root=_required_string(raw, 'source_root', scope='activation_context.workspace'),
            package_root=_required_string(raw, 'package_root', scope='activation_context.workspace'),
            data_root_status=_required_string(raw, 'data_root_status', scope='activation_context.workspace'),
            data_root_path=_optional_string(raw.get('data_root_path'), field='activation_context.workspace.data_root_path'),
            source_location_profile=_optional_string(
                raw.get('source_location_profile'), field='activation_context.workspace.source_location_profile'
            ),
            content_runtime_profile=_optional_string(
                raw.get('content_runtime_profile'), field='activation_context.workspace.content_runtime_profile'
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActivationSystemDir:
    kind: str
    directory_name: str
    path: str
    provider_class: str

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any], *, field: str) -> 'ActivationSystemDir':
        raw = _mapping(payload, field)
        _reject_unknown(raw, {'kind', 'directory_name', 'path', 'provider_class'}, field)
        return cls(
            kind=_required_string(raw, 'kind', scope=field),
            directory_name=_required_string(raw, 'directory_name', scope=field),
            path=_required_string(raw, 'path', scope=field),
            provider_class=_required_string(raw, 'provider_class', scope=field),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActivationProvidedSystemDirs:
    install_root_system_dir: ActivationSystemDir | None = None
    user_private_system_dir: ActivationSystemDir | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any] | None) -> 'ActivationProvidedSystemDirs':
        raw = _optional_mapping(payload, field='activation_context.provided_system_dirs')
        if raw is None:
            return cls()
        _reject_unknown(
            raw,
            {'install_root_system_dir', 'user_private_system_dir'},
            'activation_context.provided_system_dirs',
        )
        install_dir = raw.get('install_root_system_dir')
        user_dir = raw.get('user_private_system_dir')
        return cls(
            install_root_system_dir=(
                ActivationSystemDir.from_dict(
                    _mapping(install_dir, 'activation_context.provided_system_dirs.install_root_system_dir'),
                    field='activation_context.provided_system_dirs.install_root_system_dir',
                )
                if install_dir is not None else None
            ),
            user_private_system_dir=(
                ActivationSystemDir.from_dict(
                    _mapping(user_dir, 'activation_context.provided_system_dirs.user_private_system_dir'),
                    field='activation_context.provided_system_dirs.user_private_system_dir',
                )
                if user_dir is not None else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'install_root_system_dir': self.install_root_system_dir.to_dict() if self.install_root_system_dir else None,
            'user_private_system_dir': self.user_private_system_dir.to_dict() if self.user_private_system_dir else None,
        }


@dataclass(frozen=True, slots=True)
class ActivationRefs:
    health_snapshot_ref: str | None = None
    user_state_ref: str | None = None
    session_ref: str | None = None
    active_session_ref: str | None = None
    runtime_state_ref: str | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> 'ActivationRefs':
        raw = _mapping(payload, 'activation_context.refs')
        _reject_unknown(
            raw,
            {'health_snapshot_ref', 'user_state_ref', 'session_ref', 'active_session_ref', 'runtime_state_ref'},
            'activation_context.refs',
        )
        return cls(**{
            name: _optional_string(raw.get(name), field=f'activation_context.refs.{name}')
            for name in (
                'health_snapshot_ref', 'user_state_ref', 'session_ref',
                'active_session_ref', 'runtime_state_ref',
            )
        })

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActivationNode:
    node_id: str | None = None
    node_created_at_utc: str | None = None
    host_name: str | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any] | None) -> 'ActivationNode | None':
        raw = _optional_mapping(payload, field='activation_context.node')
        if raw is None:
            return None
        _reject_unknown(raw, {'node_id', 'node_created_at_utc', 'host_name'}, 'activation_context.node')
        return cls(
            node_id=_optional_string(raw.get('node_id'), field='activation_context.node.node_id'),
            node_created_at_utc=_optional_string(
                raw.get('node_created_at_utc'), field='activation_context.node.node_created_at_utc'
            ),
            host_name=_optional_string(raw.get('host_name'), field='activation_context.node.host_name'),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActivationUser:
    user_id: str | None = None
    account_name: str | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any] | None) -> 'ActivationUser | None':
        raw = _optional_mapping(payload, field='activation_context.user')
        if raw is None:
            return None
        _reject_unknown(raw, {'user_id', 'account_name'}, 'activation_context.user')
        return cls(
            user_id=_optional_string(raw.get('user_id'), field='activation_context.user.user_id'),
            account_name=_optional_string(raw.get('account_name'), field='activation_context.user.account_name'),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActivationSession:
    session_id: str | None = None
    session_started_at_utc: str | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any] | None) -> 'ActivationSession | None':
        raw = _optional_mapping(payload, field='activation_context.session')
        if raw is None:
            return None
        _reject_unknown(raw, {'session_id', 'session_started_at_utc'}, 'activation_context.session')
        return cls(
            session_id=_optional_string(raw.get('session_id'), field='activation_context.session.session_id'),
            session_started_at_utc=_optional_string(
                raw.get('session_started_at_utc'), field='activation_context.session.session_started_at_utc'
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActivationRuntimePackage:
    binding_id: str
    package_id: str
    package_version: str
    binding_profile: str
    environment_id: str
    relative_path: str
    payload_digest: str
    specification: Mapping[str, Any]
    platform_profile: Mapping[str, str] | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> 'ActivationRuntimePackage':
        raw = _mapping(payload, 'activation_context.runtime_packages[]')
        _reject_unknown(
            raw,
            {
                'binding_id', 'package_id', 'package_version', 'binding_profile', 'environment_id',
                'relative_path', 'payload_digest', 'specification', 'platform_profile',
            },
            'activation_context.runtime_packages[]',
        )
        specification = dict(_mapping(raw.get('specification'), 'activation_context.runtime_packages[].specification'))
        platform_raw = raw.get('platform_profile')
        platform_profile = None
        if platform_raw is not None:
            platform_profile = {
                str(key): str(value)
                for key, value in _mapping(
                    platform_raw, 'activation_context.runtime_packages[].platform_profile'
                ).items()
                if value is not None
            }
        return cls(
            binding_id=_required_string(raw, 'binding_id', scope='activation_context.runtime_packages[]'),
            package_id=_required_string(raw, 'package_id', scope='activation_context.runtime_packages[]'),
            package_version=_required_string(raw, 'package_version', scope='activation_context.runtime_packages[]'),
            binding_profile=_required_string(raw, 'binding_profile', scope='activation_context.runtime_packages[]'),
            environment_id=_required_string(raw, 'environment_id', scope='activation_context.runtime_packages[]'),
            relative_path=_required_string(raw, 'relative_path', scope='activation_context.runtime_packages[]'),
            payload_digest=_sha256(
                raw.get('payload_digest'), field='activation_context.runtime_packages[].payload_digest'
            ),
            specification=specification,
            platform_profile=platform_profile,
        )

    def to_dict(self) -> dict[str, Any]:
        result = {
            'binding_id': self.binding_id,
            'package_id': self.package_id,
            'package_version': self.package_version,
            'binding_profile': self.binding_profile,
            'environment_id': self.environment_id,
            'relative_path': self.relative_path,
            'payload_digest': self.payload_digest,
            'specification': dict(self.specification),
        }
        if self.platform_profile is not None:
            result['platform_profile'] = dict(self.platform_profile)
        return result


@dataclass(frozen=True, slots=True)
class ActiveSurface:
    surface_id: str
    entry_view: str | None = None
    declared_views: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> 'ActiveSurface':
        raw = _mapping(payload, 'activation_context.active_surface')
        _reject_unknown(raw, {'surface_id', 'entry_view', 'declared_views'}, 'activation_context.active_surface')
        return cls(
            surface_id=_required_string(raw, 'surface_id', scope='activation_context.active_surface'),
            entry_view=_optional_string(raw.get('entry_view'), field='activation_context.active_surface.entry_view'),
            declared_views=_string_tuple(
                raw.get('declared_views'), field='activation_context.active_surface.declared_views'
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'surface_id': self.surface_id,
            'entry_view': self.entry_view,
            'declared_views': list(self.declared_views),
        }


@dataclass(frozen=True, slots=True)
class ActivationFlags:
    attach_mode: str | None = None
    degraded_launch: bool = False

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any] | None) -> 'ActivationFlags':
        raw = _optional_mapping(payload, field='activation_context.activation')
        if raw is None:
            return cls()
        _reject_unknown(raw, {'attach_mode', 'degraded_launch'}, 'activation_context.activation')
        return cls(
            attach_mode=_optional_string(raw.get('attach_mode'), field='activation_context.activation.attach_mode'),
            degraded_launch=_required_bool(
                raw.get('degraded_launch', False), field='activation_context.activation.degraded_launch'
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AppActivationContext:
    contract_version: str
    generated_at_utc: str
    world_id: str
    world_display_name: str | None
    active_surface: ActiveSurface
    activation: ActivationFlags
    source_revision: SourceRevisionRef
    workspace: ActivationWorkspace
    provided_system_dirs: ActivationProvidedSystemDirs = field(default_factory=ActivationProvidedSystemDirs)
    refs: ActivationRefs = field(default_factory=ActivationRefs)
    node: ActivationNode | None = None
    user: ActivationUser | None = None
    session: ActivationSession | None = None
    available_route_groups: tuple[str, ...] = tuple()
    runtime_packages: tuple[ActivationRuntimePackage, ...] = tuple()

    @property
    def entry_view(self) -> str:
        return self.active_surface.entry_view or 'scenario_chat'

    @property
    def declared_views(self) -> tuple[str, ...]:
        return self.active_surface.declared_views

    @property
    def active_surface_id(self) -> str:
        return self.active_surface.surface_id

    @property
    def attach_mode(self) -> str:
        return self.activation.attach_mode or 'local'

    @property
    def degraded_launch(self) -> bool:
        return self.activation.degraded_launch

    @property
    def node_id(self) -> str | None:
        return self.node.node_id if self.node is not None else None

    @property
    def node_created_at_utc(self) -> str | None:
        return self.node.node_created_at_utc if self.node is not None else None

    @property
    def user_id(self) -> str | None:
        return self.user.user_id if self.user is not None else None

    @property
    def account_name(self) -> str | None:
        return self.user.account_name if self.user is not None else None

    @property
    def host_name(self) -> str | None:
        return self.node.host_name if self.node is not None else None

    @property
    def session_id(self) -> str | None:
        return self.session.session_id if self.session is not None else None

    @property
    def session_started_at_utc(self) -> str | None:
        return self.session.session_started_at_utc if self.session is not None else None

    def runtime_package_by_binding_id(self, binding_id: str) -> ActivationRuntimePackage | None:
        requested = str(binding_id).strip()
        return next((item for item in self.runtime_packages if item.binding_id == requested), None)

    def require_runtime_package(
        self,
        binding_id: str,
        *,
        package_id: str,
        binding_profile: str,
    ) -> ActivationRuntimePackage:
        item = self.runtime_package_by_binding_id(binding_id)
        if item is None:
            raise AppConfigError(f'AppDock activation context misses runtime binding `{binding_id}`')
        if item.package_id != package_id:
            raise AppConfigError(
                f'AppDock runtime binding `{binding_id}` resolves unexpected package: '
                f'{item.package_id}; expected {package_id}'
            )
        if item.binding_profile != binding_profile:
            raise AppConfigError(
                f'AppDock runtime binding `{binding_id}` has unexpected profile: '
                f'{item.binding_profile}; expected {binding_profile}'
            )
        return item

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> 'AppActivationContext':
        raw = _mapping(payload, 'activation_context')
        _reject_unknown(
            raw,
            {
                'contract_version', 'generated_at_utc', 'world', 'active_surface', 'activation',
                'source_revision', 'workspace', 'provided_system_dirs', 'refs', 'node', 'user',
                'session', 'available_route_groups', 'runtime_packages',
            },
            'activation_context',
        )
        world = _mapping(raw.get('world'), 'activation_context.world')
        _reject_unknown(world, {'world_id', 'display_name'}, 'activation_context.world')
        packages = raw.get('runtime_packages') or []
        if not isinstance(packages, (list, tuple)):
            raise AppConfigError('activation_context.runtime_packages must be an array')
        return cls(
            contract_version=_contract_version(raw.get('contract_version')),
            generated_at_utc=_required_string(raw, 'generated_at_utc', scope='activation_context'),
            world_id=_required_string(world, 'world_id', scope='activation_context.world'),
            world_display_name=_optional_string(
                world.get('display_name'), field='activation_context.world.display_name'
            ),
            active_surface=ActiveSurface.from_dict(
                _mapping(raw.get('active_surface'), 'activation_context.active_surface')
            ),
            activation=ActivationFlags.from_dict(raw.get('activation')),
            source_revision=SourceRevisionRef.from_dict(
                _mapping(raw.get('source_revision'), 'activation_context.source_revision')
            ),
            workspace=ActivationWorkspace.from_dict(
                _mapping(raw.get('workspace'), 'activation_context.workspace')
            ),
            provided_system_dirs=ActivationProvidedSystemDirs.from_dict(raw.get('provided_system_dirs')),
            refs=ActivationRefs.from_dict(_mapping(raw.get('refs'), 'activation_context.refs')),
            node=ActivationNode.from_dict(raw.get('node')),
            user=ActivationUser.from_dict(raw.get('user')),
            session=ActivationSession.from_dict(raw.get('session')),
            available_route_groups=_string_tuple(
                raw.get('available_route_groups'), field='activation_context.available_route_groups'
            ),
            runtime_packages=tuple(
                ActivationRuntimePackage.from_dict(_mapping(item, 'activation_context.runtime_packages[]'))
                for item in packages
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'contract_version': self.contract_version,
            'generated_at_utc': self.generated_at_utc,
            'world': {'world_id': self.world_id, 'display_name': self.world_display_name},
            'active_surface': self.active_surface.to_dict(),
            'activation': self.activation.to_dict(),
            'source_revision': self.source_revision.to_dict(),
            'workspace': self.workspace.to_dict(),
            'provided_system_dirs': self.provided_system_dirs.to_dict(),
            'refs': self.refs.to_dict(),
            'node': self.node.to_dict() if self.node is not None else None,
            'user': self.user.to_dict() if self.user is not None else None,
            'session': self.session.to_dict() if self.session is not None else None,
            'available_route_groups': list(self.available_route_groups),
            'runtime_packages': [item.to_dict() for item in self.runtime_packages],
        }


def get_activation_context_path_from_env() -> Path | None:
    value = os.getenv(ACTIVATION_CONTEXT_ENV, '').strip()
    return Path(value).expanduser() if value else None


def get_appdock_config_path_from_env() -> Path | None:
    value = os.getenv(APPDOCK_CONFIG_ENV, '').strip()
    return Path(value).expanduser() if value else None


def load_activation_context(path: Path) -> AppActivationContext:
    candidate = Path(path).expanduser()
    try:
        payload = json.loads(candidate.read_text(encoding='utf-8'))
    except Exception as exc:
        raise AppConfigError(f'Failed to read AppDock activation context: {candidate}') from exc
    try:
        return AppActivationContext.from_dict(_mapping(payload, 'activation_context'))
    except AppConfigError:
        raise
    except Exception as exc:
        raise AppConfigError(f'Invalid AppDock activation context: {candidate}: {exc}') from exc


def load_activation_context_from_env() -> AppActivationContext | None:
    path = get_activation_context_path_from_env()
    if path is None:
        return None
    return load_activation_context(path)


__all__ = [
    'ACTIVATION_CONTEXT_CONTRACT_VERSION',
    'ACTIVATION_CONTEXT_ENV',
    'APPDOCK_CONFIG_ENV',
    'ActivationFlags',
    'ActivationProvidedSystemDirs',
    'ActivationRefs',
    'ActivationRuntimePackage',
    'ActivationSession',
    'ActivationSystemDir',
    'ActivationUser',
    'ActivationWorkspace',
    'ActiveSurface',
    'AppActivationContext',
    'SourceRevisionRef',
    'get_activation_context_path_from_env',
    'get_appdock_config_path_from_env',
    'load_activation_context',
    'load_activation_context_from_env',
]
