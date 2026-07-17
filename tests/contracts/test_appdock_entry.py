from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from stratbox_windows.adapters.appdock.entry import main, validate_appdock_runtime_contract
from stratbox_windows.adapters.appdock.runtime_contracts import AppActivationContext
from stratbox_windows.runtime.errors import AppConfigError


def test_entry_validates_declared_distribution_bindings(appdock_activation_payload: dict) -> None:
    context = AppActivationContext.from_dict(appdock_activation_payload)

    validate_appdock_runtime_contract(context)


def test_entry_delegates_without_mutating_sys_path(
    tmp_path: Path,
    monkeypatch,
    appdock_activation_payload: dict,
) -> None:
    activation_path = tmp_path / 'activation.json'
    activation_path.write_text(json.dumps(appdock_activation_payload), encoding='utf-8')
    monkeypatch.setenv('APPDOCK_ACTIVATION_CONTEXT_PATH', str(activation_path))

    captured: dict[str, object] = {}

    def fake_main(argv, *, launch_origin):
        captured['argv'] = argv
        captured['launch_origin'] = launch_origin
        return 17

    monkeypatch.setattr('stratbox_windows.__main__.main', fake_main)
    original_path = list(sys.path)

    assert main(['--diagnose']) == 17
    assert captured == {'argv': ['--diagnose'], 'launch_origin': 'appdock'}
    assert sys.path == original_path


def test_entry_rejects_missing_core_runtime_binding(appdock_activation_payload: dict) -> None:
    appdock_activation_payload['runtime_packages'] = [
        item
        for item in appdock_activation_payload['runtime_packages']
        if item['binding_id'] != 'stratbox-core-python'
    ]
    context = AppActivationContext.from_dict(appdock_activation_payload)

    with pytest.raises(AppConfigError, match='stratbox-core-python'):
        validate_appdock_runtime_contract(context)


def test_entry_returns_safe_error_for_invalid_runtime_graph(
    tmp_path: Path,
    monkeypatch,
    capsys,
    appdock_activation_payload: dict,
) -> None:
    appdock_activation_payload['runtime_packages'] = []
    activation_path = tmp_path / 'activation.json'
    activation_path.write_text(json.dumps(appdock_activation_payload), encoding='utf-8')
    monkeypatch.setenv('APPDOCK_ACTIVATION_CONTEXT_PATH', str(activation_path))

    assert main([]) == 2
    assert 'ERROR:' in capsys.readouterr().out


def test_runtime_contract_rejects_wrong_world_or_surface(appdock_activation_payload: dict) -> None:
    appdock_activation_payload['world']['world_id'] = 'other'
    context = AppActivationContext.from_dict(appdock_activation_payload)
    with pytest.raises(AppConfigError, match='unexpected world'):
        validate_appdock_runtime_contract(context)

    appdock_activation_payload['world']['world_id'] = 'stratbox'
    appdock_activation_payload['active_surface']['surface_id'] = 'other'
    context = AppActivationContext.from_dict(appdock_activation_payload)
    with pytest.raises(AppConfigError, match='unexpected surface'):
        validate_appdock_runtime_contract(context)
