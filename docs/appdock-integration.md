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

Для актуального AppDock Strategy Box Windows должен жить как конечный desktop product:

- primary source: `stratbox-windows`
- primary source form: `runtime_snapshot`
- primary source entry mode: `preset_locked`
- primary source locator: GitHub clone URL `stratbox-windows`
- primary source ref: branch `main`
- primary source refresh policy: `on_launch`
- additional package source: `stratbox`
- package refresh policy: `on_launch`
- install mode: `machine_managed_install`
- post-setup entry: `direct_entry_surface`

Это означает, что Runtime Shell не должен запрашивать repo source у пользователя. Источник зафиксирован preset-ом, а AppDock сам:

1. refresh-ит primary source cache;
2. materialize-ит актуальный runtime snapshot для `stratbox-windows`;
3. refresh-ит и materialize-ит дополнительный package source `stratbox`;
4. применяет installation recipe для package source;
5. запускает primary desktop surface Strategy Box.

## Package composition

В `appdock/preset.json` core-репозиторий оформлен через `package_composition.package_sources`.

Core должен оставаться:

- дополнительным package source;
- packaged snapshot input;
- runtime dependency для AppDock-managed runtime environment;
- `installation_recipe.editable = false`.

То есть `stratbox` остаётся частью product shape, но не подменяет primary world surface repository.

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
- `workspace.bundle_root`
- `workspace.install_root`
- `workspace.system_root`

Но для самого приложения главным входом остаётся `workspace.primary_root`.

## Что здесь важно не сломать

- `manifest.json` и `preset.json` должны оставаться согласованными;
- repo не должен снова начать тащить локальную копию `stratbox`;
- `stratbox` должен оставаться отдельным package source, а не встроенной копией исходников;
- AppDock-specific код должен оставаться в `adapters/appdock`, а не расползаться по всему runtime;
- конечный product mode не должен откатываться обратно к legacy attached/user-selected repo source routes;
- системная установка должна оставаться machine-managed и platform-managed по roots/данным.
