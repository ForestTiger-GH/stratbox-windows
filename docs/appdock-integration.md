# Связка с AppDock

## Роль репозитория

`stratbox-windows` — это primary AppDock surface repository для Strategy Box на Windows.

Он содержит:
- `appdock/manifest.json`
- `appdock/preset.json`
- Python entrypoint для surface
- runtime/application/presentation слои приложения

Он **не содержит** core-пакет `stratbox` внутри себя.

## Как AppDock должен мыслить этот продукт

- primary repo: `stratbox-windows`
- bundled runtime dependency: `stratbox`

В `appdock/preset.json` это оформлено через `bundle_composition.auxiliary_sources`. Core должен materialize-иться AppDock и ставиться в managed environment как runtime dependency.

## Что должно быть уже готово в AppDock

AppDock должен уметь:
- materialize bundled repos;
- включать их в install graph;
- ставить bundled repos в managed `.venv`;
- запускать primary surface через activation target без костылей через `PYTHONPATH=primary/src`.

## Activation target

Surface запускается через:

- `stratbox_windows.adapters.appdock.entry`

Это thin boundary entrypoint, который должен оставаться максимально тонким и не превращаться во второй runtime engine.

## Что здесь важно не сломать

- `manifest.json` и `preset.json` должны оставаться согласованными;
- repo не должен снова начать тащить локальную копию `stratbox`;
- bundled dependency на `stratbox` должна оставаться частью product shape;
- AppDock-specific код должен оставаться в `adapters/appdock`, а не расползаться по всему runtime.
