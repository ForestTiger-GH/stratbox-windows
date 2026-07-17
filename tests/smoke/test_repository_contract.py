from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _manifest() -> dict:
    return json.loads((ROOT / 'appdock' / 'manifest.json').read_text(encoding='utf-8'))


def test_repository_uses_single_connector_manifest() -> None:
    assert (ROOT / 'appdock' / 'manifest.json').is_file()
    assert not (ROOT / 'appdock' / 'preset.json').exists()


def test_manifest_declares_connector_3_strategy_box_world() -> None:
    manifest = _manifest()

    assert manifest['contract_version'] == '3.0'
    assert manifest['identity']['world_id'] == 'stratbox'
    assert manifest['identity']['world_name'] == 'Strategy Box'
    assert manifest['identity']['world_version'] == '0.1.0'
    assert manifest['default_surface_id'] == 'desktop'
    assert set(manifest) == {
        'contract_version',
        'identity',
        'world_definition',
        'source_requirements',
        'package_declarations',
        'runtime_bindings',
        'default_surface_id',
        'surfaces',
        'capabilities',
        'requirements',
        'hooks',
        'extensions',
    }


def test_manifest_enables_data_without_preselecting_binding() -> None:
    definition = _manifest()['world_definition']

    assert definition == {'data_profile': 'data_enabled'}


def test_manifest_declares_external_stratbox_core_source() -> None:
    requirements = _manifest()['source_requirements']

    assert len(requirements) == 1
    requirement = requirements[0]
    assert requirement['source_id'] == 'stratbox_core_source'
    assert requirement['source_ref'] == 'https://github.com/ForestTiger-GH/stratbox.git'
    assert requirement['access']['authentication'] == 'anonymous_allowed'
    assert requirement['materialization']['clone_strategy'] == 'checkout'


def test_manifest_declares_exact_python_projects_and_binding_graph() -> None:
    manifest = _manifest()
    packages = {item['package_ref']: item for item in manifest['package_declarations']}
    bindings = {item['binding_id']: item for item in manifest['runtime_bindings']}

    assert packages['stratbox_windows_package']['source_id'] == 'manifest_source'
    assert packages['stratbox_windows_package']['package_identity'] == {
        'package_id': 'stratbox-windows',
        'package_version': '0.1.0',
    }
    assert packages['stratbox_core_package']['source_id'] == 'stratbox_core_source'
    assert packages['stratbox_core_package']['package_identity'] == {
        'package_id': 'stratbox',
        'package_version': '0.2.1',
    }
    assert bindings['stratbox-core-python']['binding_profile'] == 'runtime_binding_python_distribution'
    assert bindings['stratbox-windows-python']['binding_profile'] == 'runtime_binding_python_distribution'
    assert bindings['stratbox-windows-python']['depends_on'] == ['stratbox-core-python']
    assert {item['environment_id'] for item in bindings.values()} == {'world'}


def test_manifest_declares_activation_4_desktop_entrypoint() -> None:
    surface = _manifest()['surfaces'][0]
    activation = surface['activation']
    entrypoint = activation['entrypoint']

    assert surface['surface_id'] == 'desktop'
    assert surface['entry_view'] == 'scenario_chat'
    assert activation['contract_version'] == '4.0'
    assert entrypoint['kind'] == 'python_module'
    assert entrypoint['target'] == 'stratbox_windows.adapters.appdock.entry'
    assert entrypoint['target_binding_id'] == 'stratbox-windows-python'
    assert entrypoint['cwd_policy']['binding_id'] == 'stratbox-windows-python'
    assert entrypoint['env_policy'] == {'mode': 'sanitized'}
    assert activation['diagnostics'] == {
        'strategy': 'same_entrypoint_with_args',
        'args': ['--diagnose'],
        'timeout_seconds': 30,
    }


def test_manifest_contains_no_legacy_connector_vocabulary() -> None:
    text = json.dumps(_manifest(), sort_keys=True)

    for forbidden in (
        'package_mounts',
        'source_packaging_profile',
        'mount_id',
        '"kind": "python_module", "target"',
        '"strategy": "flag"',
    ):
        assert forbidden not in text


def test_manifest_versions_match_python_project_metadata() -> None:
    import tomllib

    pyproject = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))
    manifest = _manifest()
    packages = {item['package_ref']: item for item in manifest['package_declarations']}

    assert pyproject['project']['version'] == manifest['identity']['world_version']
    assert pyproject['project']['version'] == (
        packages['stratbox_windows_package']['package_identity']['package_version']
    )
    assert 'stratbox==0.2.1' in pyproject['project']['dependencies']
    assert packages['stratbox_core_package']['package_identity']['package_version'] == '0.2.1'
