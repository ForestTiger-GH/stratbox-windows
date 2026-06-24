from __future__ import annotations

def test_external_stratbox_dependency_is_importable() -> None:
    import stratbox  # noqa: F401

    from stratbox.base.filestore import FileStore

    assert FileStore is not None
