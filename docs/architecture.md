# Архитектура stratbox-windows

`stratbox-windows` — это отдельный product surface repository. Он содержит Windows desktop surface для Strategy Box и **не содержит** библиотечное ядро внутри себя.

## Что считается правильной границей

- `stratbox` — внешний core package и bundled runtime dependency.
- `stratbox-windows` — primary AppDock surface repo.
- `AppDock` — внешний runtime/productization/deployment контур.

Внутри `stratbox-windows` не должны появляться:
- копия `src/stratbox`;
- библиотечные example scripts из core;
- runtime state (`.tmp`, `.venv`, build outputs, generated artifacts`);
- ad hoc интеграции, которые относятся к AppDock engine, а не к самому surface.

## Слои внутри `src/stratbox_windows`

### `application`
Прикладная логика surface:
- сценарии;
- кейсы;
- события;
- логи;
- артефакты;
- поручения;
- background orchestration;
- workspace-level use cases.

Этот слой описывает поведение Strategy Box как рабочей поверхности и не должен тянуть Qt-виджеты или прямую AppDock-специфику.

### `runtime`
Сборка runtime-состояния приложения:
- context;
- paths;
- config;
- session runtime;
- logging;
- version;
- bootstrap.

Это композиционный слой surface. Он может знать про запуск и окружение, но должен оставаться отдельно от конкретных UI-виджетов.

### `adapters/appdock`
Boundary к AppDock:
- activation contract parsing;
- AppDock entrypoint;
- bridge к runtime;
- surface-state reporting.

Здесь живёт всё, что относится именно к внешнему AppDock-контракту.

### `adapters/desktop_host`
Boundary к desktop host:
- open path;
- clipboard / shell integration;
- прочие ОС-специфические сервисы.

### `presentation/common`
Общие presentation-модели:
- projector;
- semantic view-models;
- form specs;
- scenario-chat models.

Это presentation semantics без жёсткой привязки к Qt.

### `presentation/qt_desktop`
Конкретная реализация на PySide6/Qt:
- main window;
- panels;
- dialogs;
- widgets;
- shell;
- coordinators;
- workers.

## Что считать нормой для дальнейшей разработки

- Новые AppDock-boundary изменения должны идти в `adapters/appdock`, а не в `runtime`.
- Новые desktop-host сервисы должны идти в `adapters/desktop_host`.
- Если кусок можно описать как presentation semantics без Qt, он должен жить в `presentation/common`.
- Если код требует виджетов/Qt signals/Qt event loop, он живёт в `presentation/qt_desktop`.
- Любая бизнес-/core-логика должна уходить в `stratbox`, а не возвращаться в `stratbox-windows`.
