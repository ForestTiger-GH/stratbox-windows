# Strategy Box Windows App Surface

Пакет `stratbox_windows` — это Windows desktop surface для Strategy Box.

## Архитектурные слои

- `application` — прикладная логика surface.
- `runtime` — runtime assembly и состояние.
- `adapters/appdock` — вход и интеграция через AppDock.
- `adapters/desktop_host` — работа с desktop host.
- `presentation/common` — общие presentation-модели.
- `presentation/qt_desktop` — конкретный UI на PySide6.

Пакет зависит от внешнего `stratbox` и больше не содержит внутри себя библиотечное ядро.
