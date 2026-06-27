# Strategy Box Windows

Strategy Box Windows — primary Windows desktop surface для запуска аналитических сценариев Strategy Box поверх AppDock-managed рабочей среды.

Репозиторий содержит только приложение, AppDock connector и desktop/runtime-слой. Библиотечное ядро и доменные пакеты поставляются отдельно через зависимость `stratbox` и в AppDock-сценарии приезжают как bundled runtime dependency.

## Что внутри

- `src/stratbox_windows/application` — прикладная логика surface: сценарии, кейсы, логи, артефакты, фон, поручения.
- `src/stratbox_windows/runtime` — runtime-композиция приложения.
- `src/stratbox_windows/adapters/appdock` — AppDock boundary.
- `src/stratbox_windows/adapters/desktop_host` — desktop-host adapter.
- `src/stratbox_windows/presentation/common` — общие presentation-модели.
- `src/stratbox_windows/presentation/qt_desktop` — конкретная Qt desktop-реализация.

## Локальный запуск для разработки

Сначала в то же виртуальное окружение должен быть установлен `stratbox`:

```bash
python -m pip install -e ../stratbox
python -m pip install -e .
```

После этого можно запускать приложение:

```bash
python -m stratbox_windows --standalone-dev-root ./.tmp/dev-workspace
```

Диагностика:

```bash
python -m stratbox_windows --standalone-dev-root ./.tmp/dev-workspace --diagnose
```

## AppDock

`appdock/manifest.json` объявляет primary desktop surface `stratbox_windows.desktop`.

`appdock/preset.json` описывает Strategy Box как конечный product-mode выпуск для AppDock:

- primary source = `stratbox-windows`;
- source form = `runtime_snapshot`;
- entry mode = `preset_locked`;
- fixed locator = GitHub clone URL этого репозитория;
- ref = `main`;
- refresh policy = `on_launch`;
- auxiliary bundled source = `stratbox-core`.

Это означает, что Runtime Shell не должен запрашивать у пользователя внешний репозиторий вручную. AppDock сам держит primary source cache, обновляет его при запуске, materialize-ит актуальный runtime snapshot и отдельно ставит bundled dependency `stratbox` в AppDock-managed runtime environment.

## Документация

- `docs/architecture.md` — архитектурная карта репозитория и границы слоёв.
- `docs/development.md` — локальная разработка, установка зависимостей и проверка запуска.
- `docs/appdock-integration.md` — связка с AppDock и bundled runtime dependency `stratbox`.

## Минимальные проверки

Репозиторий содержит минимальный test/smoke-контур и проверки структуры:

```bash
python scripts/check_release_integrity.py
python scripts/check_internal_imports.py
python -m pytest
```

Для smoke-проверок, связанных с core, в окружении должен быть доступен пакет `stratbox`.
