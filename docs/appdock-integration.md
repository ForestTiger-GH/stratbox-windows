# Связка с AppDock

## Роль репозитория

`stratbox-windows` — primary AppDock surface repository для Strategy Box на Windows.

Он содержит:
- `appdock/manifest.json`;
- `appdock/preset.json`;
- Python entrypoint для surface;
- runtime/application/presentation слои приложения.

Он **не содержит** core-пакет `stratbox` внутри себя.

## Как AppDock должен мыслить этот продукт

Для актуального AppDock Strategy Box Windows должен жить как конечный Windows desktop product с preset-определённой доставкой:

- `platform_profile = platform_windows`;
- `output_format_profile = output_format_exe`;
- `install_profile = install_local_system`;
- `source_profile = source_preset`;
- `update_profile = update_start_force`;
- `node_profile = node_disabled`;
- `data_profile = data_enabled`;
- `data_location_profile = data_location_local_preset`;
- `welcome_profile = welcome_banner`;
- `entry_profile = entry_direct`.

Это означает, что Runtime Shell не должен просить конечного пользователя выбирать репозитории вручную. Источники задаются preset-ом, а AppDock сам:

1. materialize-ит и refresh-ит primary source `stratbox-windows` при каждом запуске;
2. materialize-ит и refresh-ит secondary source `stratbox` при каждом запуске;
3. применяет `installation_recipe` для secondary source;
4. запускает primary desktop surface Strategy Box из AppDock-managed runtime.

## Source composition

В `appdock/preset.json` оба репозитория теперь живут в едином `source_composition.sources`.

### Manifest-bearing primary source
`stratbox-windows` должен оставаться:

- primary source продукта;
- manifest-bearing source с `source_manifest_state = source_manifest_included`;
- remote source с `source_location_profile = source_location_remote`;
- installable source с `source_packaging_profile = source_packaging_installable`.

Именно этот source определяет world identity, surfaces и AppDock-facing activation contract.

### Secondary source
`stratbox` должен оставаться:

- secondary source с `source_manifest_state = source_manifest_none`;
- отдельным `mount_id = stratbox`;
- remote source;
- installable source;
- runtime dependency для AppDock-managed environment;
- source с `installation_recipe.mode = pip` и `editable = false`.

То есть `stratbox` остаётся частью product shape, но не подменяет manifest-bearing primary world source.

## Derived package/update semantics

Так как и primary, и secondary sources заданы как `source_packaging_installable`, AppDock должен выводить:

- `packages_profile = packages_installable`;
- source refresh на каждом запуске;
- package refresh на каждом запуске;
- fallback в локально materialized состояние при проблемах refresh, если AppDock runtime считает это допустимым.

Это и есть правильная геометрия для рабочего экономического приложения, которое должно системно устанавливаться и всегда обновляться при старте.

## Activation target

Surface запускается через:

- `stratbox_windows.adapters.appdock.entry`

Это thin boundary entrypoint, который должен оставаться максимально тонким и не превращаться во второй runtime engine.

## Runtime handoff contract

На AppDock boundary каноническое поле рабочего корня сейчас называется:

- `workspace.primary_root`

Именно это поле Strategy Box Windows должен читать из activation context. Внутри собственного runtime слоя это поле маппится в локальное понятие:

- `product_root`

То есть:

- AppDock vocabulary остаётся снаружи;
- внутренняя модель surface не копирует boundary-термины буквально;
- старое ожидание `workspace.source_root` в product mode больше не используется.

Дополнительно activation context всё ещё может нести:
- `workspace.bundle_root`;
- `workspace.install_root`;
- `workspace.system_root`.

Но для самого приложения главным входом остаётся `workspace.primary_root`.

## Data posture

Для Strategy Box data-sector является частью продукта.

Значит, preset должен явно удерживать:

- `feature_data_enabled = true`;
- `data_profile = data_enabled`;
- `data_location_profile = data_location_local_preset`.

Это означает, что AppDock должен рассматривать data root как локальную product-managed часть среды, а не как отключённый или полностью свободный пользовательский сектор.

## Что здесь важно не сломать

- `manifest.json` и `preset.json` должны оставаться согласованными;
- repo не должен снова начать тащить локальную копию `stratbox`;
- `stratbox` должен оставаться отдельным secondary source, а не встроенной копией исходников;
- AppDock-specific код должен оставаться в `adapters/appdock`, а не расползаться по всему runtime;
- конечный product mode не должен откатываться обратно к legacy `primary_source + package_composition` модели;
- системная установка должна оставаться `install_local_system`;
- always-refresh поведение должно выражаться через `update_profile = update_start_force`, а не через старый ручной `update_policy` блок.
