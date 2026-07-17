# Strategy Box Windows

Strategy Box Windows — основной Windows desktop surface для запуска Strategy Box в AppDock-managed рабочей среде.

Репозиторий содержит:
- конечный desktop surface продукта;
- AppDock Connector Manifest `3.0`;
- строгий адаптер Activation Context `3.0`;
- runtime/application/presentation слои Windows-приложения.

Библиотечное ядро `stratbox` остаётся отдельным репозиторием. В AppDock product mode оно объявляется как обязательный secondary source, материализуется как отдельный Python project package и устанавливается в тот же managed environment раньше `stratbox-windows`.

## Что внутри

- `src/stratbox_windows/application` — прикладная логика surface: сценарии, кейсы, логи, артефакты, фоновые процессы, поручения.
- `src/stratbox_windows/runtime` — runtime-композиция приложения.
- `src/stratbox_windows/adapters/appdock` — строгая граница AppDock Connector/Activation Context.
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

`appdock/manifest.json` является единственной repo-local декларацией Strategy Box. Connector `3.0` фиксирует:

- `world_id = stratbox` и имя мира `Strategy Box`;
- desktop surface `desktop`;
- Activation contract `4.0` и entrypoint `stratbox_windows.adapters.appdock.entry`;
- включённый Data sector без заранее выбранного locator/binding;
- secondary source `stratbox`;
- package declarations для `stratbox` и `stratbox-windows`;
- dependency-ordered bindings `runtime_binding_python_distribution` в едином environment `world`.

AppDock materialize-ит оба source package, создаёт managed Python environment, устанавливает сначала `stratbox`, затем `stratbox-windows`, после чего запускает surface через Activation Context `3.0`.

Временный механизм `activation_context.package_mounts` удалён. Импорт `stratbox` должен обеспечиваться штатной установкой runtime binding, а не изменением `sys.path` в entrypoint.

Параметры установки, обновления, размещения Data, оформления и входа выбираются в AppDock Studio. Отдельный `appdock/preset.json` отсутствует.

## Документация

- `docs/architecture.md` — архитектурная карта репозитория и границы слоёв.
- `docs/development.md` — локальная разработка, установка зависимостей и проверка запуска.
- `docs/appdock-integration.md` — Connector `3.0`, package graph и Activation Context `3.0`.

## Минимальные проверки

```bash
python scripts/check_release_integrity.py
python scripts/check_internal_imports.py
python scripts/check_appdock_contract.py --appdock-repository ../AppDock
python -m pytest
```

Для smoke-проверок, связанных с core, в окружении должен быть доступен пакет `stratbox`.
