# Связка с AppDock

## Роль репозитория

`stratbox-windows` — primary AppDock surface repository для Strategy Box на Windows.

Он содержит:
- `appdock/manifest.json`
- `appdock/preset.json`
- Python entrypoint для surface
- runtime/application/presentation слои приложения

Он **не содержит** core-пакет `stratbox` внутри себя.

## Как AppDock должен мыслить этот продукт

Для актуального AppDock Strategy Box Windows должен жить как product-mode desktop world:

- primary repo: `stratbox-windows`
- primary source form: `runtime_snapshot`
- primary source entry mode: `preset_locked`
- primary source locator: GitHub clone URL `stratbox-windows`
- primary source ref: branch `main`
- primary source refresh policy: `on_launch`
- bundled runtime dependency: `stratbox`

Это означает, что Runtime Shell не должен запрашивать repo source у пользователя. Источник зафиксирован preset-ом, а AppDock сам:

1. refresh-ит primary source cache;
2. materialize-ит актуальный runtime snapshot;
3. materialize-ит auxiliary bundled source `stratbox-core`;
4. ставит bundled dependency в AppDock-managed runtime environment;
5. запускает primary surface.

## Bundle composition

В `appdock/preset.json` core-репозиторий оформлен через `bundle_composition.auxiliary_sources`.

Core должен оставаться:

- auxiliary bundled source;
- bundled snapshot input;
- runtime dependency для AppDock-managed runtime environment;
- `runtime_install_editable = false`.

То есть `stratbox` остаётся частью product shape, но не подменяет primary world surface repository.

## Activation target

Surface запускается через:

- `stratbox_windows.adapters.appdock.entry`

Это thin boundary entrypoint, который должен оставаться максимально тонким и не превращаться во второй runtime engine.

## Runtime handoff contract

На AppDock boundary каноническое поле рабочего корня теперь называется:

- `workspace.primary_root`

Именно это поле Strategy Box Windows должен читать из activation context. Внутри собственного runtime слоя это поле маппится в локальное понятие:

- `product_root`

То есть:

- AppDock vocabulary остаётся снаружи;
- внутренняя модель surface не копирует boundary-термины буквально;
- старое ожидание `workspace.source_root` считается устаревшим и в продуктовый режим больше не входит.

## Что здесь важно не сломать

- `manifest.json` и `preset.json` должны оставаться согласованными;
- repo не должен снова начать тащить локальную копию `stratbox`;
- bundled dependency на `stratbox` должна оставаться частью product shape;
- AppDock-specific код должен оставаться в `adapters/appdock`, а не расползаться по всему runtime;
- конечный product mode не должен откатываться обратно к `attached_source` или к user-selected repo source.
