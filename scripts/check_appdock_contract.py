"""Validate Strategy Box Windows against an exact AppDock checkout."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Validate stratbox-windows Connector against an AppDock repository checkout.'
    )
    parser.add_argument(
        '--appdock-repository',
        required=True,
        type=Path,
        help='Path to the AppDock repository root.',
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    appdock_root = args.appdock_repository.expanduser().resolve()
    appdock_src = appdock_root / 'src'
    if not (appdock_src / 'appdock').is_dir():
        print(f'ERROR: AppDock source package is unavailable: {appdock_src}')
        return 2
    sys.path.insert(0, str(appdock_src))

    from appdock.domains.world.sources.manifest_admission import admit_manifest_declaration
    from appdock.domains.world.surfaces.activation_targets import activation_target_exists
    from appdock.interop.contracts.world import ConnectorManifest

    manifest_path = ROOT / 'appdock' / 'manifest.json'
    try:
        payload = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest = ConnectorManifest.from_dict(payload)
        admission = admit_manifest_declaration(manifest.declaration)
        if not admission.ok:
            for issue in admission.issues:
                print(f'ERROR: {issue.code}: {issue.message}')
            return 1
        if not activation_target_exists(ROOT, manifest.default_surface.activation):
            print(
                'ERROR: default activation target is unavailable: '
                + manifest.default_surface.activation.entrypoint.target
            )
            return 1
    except Exception as exc:
        print(f'ERROR: Connector validation failed: {type(exc).__name__}: {exc}')
        return 1

    print(f'OK Connector {manifest.contract_version}: {manifest.identity.world_id}')
    print(f'OK authority surface: {manifest.default_surface_id}')
    print('OK source requirements: ' + ', '.join(item.source_id for item in manifest.source_requirements))
    print('OK runtime bindings: ' + ', '.join(item.binding_id for item in manifest.runtime_bindings))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
