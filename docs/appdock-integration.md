# Связка с AppDock

## Минимальный проверочный контракт

`stratbox-windows` подключается к AppDock через единственный repo-local connector:

- `appdock/manifest.json`.

Отдельный `appdock/preset.json` больше не используется. Параметры конкретного выпуска, установки и поведения Shell выбираются в Studio и входят в итоговый `WorldDefinition`.

Connector фиксирует только обязательные свойства самого мира:

- `world_id = stratbox`;
- `world_name = Strategy Box`;
- основная surface `desktop`;
- Python entrypoint `stratbox_windows.adapters.appdock.entry`;
- включённый сектор Data;
- внешний source `stratbox` как предметное ядро.

Параметры размещения Data намеренно отсутствуют. Studio должна предложить выбрать:

- локальное или удалённое размещение;
- пользовательскую или preset-привязку;
- locator, когда выбран preset-вариант.

## Репозитории

`stratbox-windows` остаётся manifest-bearing primary source и содержит desktop surface.

`stratbox` остаётся отдельным auxiliary source с `mount_id = stratbox`. Он содержит бизнес-логику и не копируется внутрь Windows-репозитория.

До появления полного installation binding для auxiliary Python packages AppDock может передать materialized source через `activation_context.package_mounts`. Entry-point Strategy Box использует этот mount как безопасный fallback как проверочный runtime fallback до появления штатного installation binding auxiliary Python packages.

## Activation context

Strategy Box читает актуальные поля workspace:

- `install_root`;
- `system_root`;
- `package_root`;
- `data_root_status`;
- `data_root_path` при настроенной Data;
- `primary_root`;
- `primary_source_location_profile`;
- `primary_content_runtime_profile`.

Старые поля `bundle_root` и `primary_form` больше не поддерживаются.

## Проверочный сценарий

1. Studio импортирует репозиторий `stratbox-windows` и читает connector manifest.
2. Разработчик выбирает недостающие параметры WorldDefinition.
3. Для Data выбирается способ привязки и каталог.
4. AppDock materialize-ит primary source и auxiliary source `stratbox`.
5. AppDock формирует activation context.
6. Сначала может быть выполнен `--diagnose`, затем обычный запуск surface `desktop`.
