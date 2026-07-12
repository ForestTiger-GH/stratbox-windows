# Strategy Box Windows

Strategy Box Windows — основной Windows desktop surface для запуска Strategy Box поверх AppDock-managed рабочей среды.

Репозиторий содержит:
- конечный desktop surface продукта;
- минимальный AppDock connector;
- runtime/application/presentation слои Windows-приложения.

Библиотечное ядро `stratbox` внутрь репозитория не встраивается. Для AppDock product mode оно подключается как **дополнительный package source** с бизнес-логикой.

## Что внутри

- `src/stratbox_windows/application` — прикладная логика surface: сценарии, кейсы, логи, артефакты, фоновые процессы, поручения.
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

## AppDock product mode

`appdock/manifest.json` является единственной repo-local декларацией Strategy Box. Он фиксирует минимум:

- `world_id = stratbox`;
- имя мира `Strategy Box`;
- desktop surface `desktop`;
- AppDock entrypoint;
- включённый Data sector;
- auxiliary source `stratbox`.

Параметры установки, обновления, размещения Data, оформления и входа выбираются в AppDock Studio. Отдельный `appdock/preset.json` отсутствует.

До появления штатной установки auxiliary Python package entrypoint подхватывает materialized source `stratbox` из `activation_context.package_mounts`.

## Документация

- `docs/architecture.md` — архитектурная карта репозитория и границы слоёв.
- `docs/development.md` — локальная разработка, установка зависимостей и проверка запуска.
- `docs/appdock-integration.md` — связка с AppDock product mode и package-source модель.

## Минимальные проверки

```bash
python scripts/check_release_integrity.py
python scripts/check_internal_imports.py
python -m pytest
```

Для smoke-проверок, связанных с core, в окружении должен быть доступен пакет `stratbox`.
