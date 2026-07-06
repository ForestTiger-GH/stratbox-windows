# Strategy Box Windows

Strategy Box Windows — основной Windows desktop surface для запуска Strategy Box поверх AppDock-managed рабочей среды.

Репозиторий содержит:
- конечный desktop surface продукта;
- AppDock connector и product preset;
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

`appdock/manifest.json` объявляет primary desktop surface `stratbox_windows.desktop`.

`appdock/preset.json` описывает Strategy Box как конечный product-mode выпуск для AppDock:

- primary source = `stratbox-windows`;
- source form = `runtime_snapshot`;
- entry mode = `preset_locked`;
- fixed locator = GitHub clone URL этого репозитория;
- ref = `main`;
- source refresh policy = `on_launch`;
- additional package source = `stratbox`;
- package refresh policy = `on_launch`;
- install mode = `machine_managed_install`;
- post-setup entry = `direct_entry_surface`.

Это означает:

1. Runtime Shell не запрашивает внешний репозиторий у пользователя вручную.
2. AppDock сам поддерживает primary source cache для `stratbox-windows`.
3. AppDock на каждом запуске пытается refresh-ить:
   - основной product source `stratbox-windows`;
   - дополнительный package source `stratbox`.
4. После готовности среды Shell ведёт пользователя прямо в основной surface Strategy Box, а не в shell-home.
5. `stratbox` остаётся отдельным package source с бизнес-логикой и materialize-ится через installation recipe, а не как встроенная копия исходников.

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
