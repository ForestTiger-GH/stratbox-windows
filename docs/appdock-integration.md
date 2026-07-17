# Связка Strategy Box Windows с AppDock

## 1. Источник истины

`stratbox-windows` подключается к AppDock через единственный repo-local connector:

- `appdock/manifest.json` — Connector Manifest contract `3.0`.

Отдельный `appdock/preset.json` не используется. Connector фиксирует собственную идентичность, состав source/package/runtime graph и desktop surface. Параметры конкретного выпуска, установки, Data binding, обновления, оформления и Shell выбираются в Studio и входят в итоговый `WorldDefinition`.

## 2. Роли репозиториев

### `stratbox-windows`

Manifest-bearing primary source:

- содержит Connector Manifest;
- содержит desktop surface;
- содержит AppDock entrypoint;
- объявляет Python project package `stratbox-windows@0.1.0`.

### `stratbox`

Обязательный secondary source:

- содержит предметное и инфраструктурное ядро;
- объявляется через `source_requirements.stratbox_core_source`;
- материализуется как отдельный Python project package `stratbox@0.2.1`;
- не содержит второго AppDock manifest и не конкурирует за роль authority.

## 3. Package и runtime binding graph

Connector объявляет два package:

```text
stratbox_core_package
  source: stratbox_core_source
  identity: stratbox@0.2.1

stratbox_windows_package
  source: manifest_source
  identity: stratbox-windows@0.1.0
```

Оба package подключаются через `runtime_binding_python_distribution`:

```text
stratbox-core-python
        ↓
stratbox-windows-python
```

`stratbox-windows-python.depends_on = [stratbox-core-python]`. Оба binding используют `environment_id = world`. Поэтому AppDock устанавливает core раньше desktop package, а обычный `import stratbox` работает через managed Python environment.

Временный `package_mounts`/`sys.path` fallback удалён. Отсутствие core binding считается нарушением runtime contract и останавливает запуск с управляемой ошибкой.

## 4. Surface activation

Desktop surface использует Activation contract `4.0`:

- kind: `python_module`;
- target: `stratbox_windows.adapters.appdock.entry`;
- target binding: `stratbox-windows-python`;
- working directory: package root этого binding;
- environment policy: `sanitized`;
- diagnostics: тот же entrypoint с аргументом `--diagnose`;
- locality: `local`;
- launch mode: `foreground`.

## 5. Activation Context `3.0`

`src/stratbox_windows/adapters/appdock/runtime_contracts.py` является stdlib-only строгим consumer adapter. Он принимает только точную версию `3.0`, запрещает неизвестные поля и проверяет runtime package digests.

Актуальные workspace-поля:

- `install_root`;
- `user_workspace_root`;
- `system_root`;
- `source_root`;
- `package_root`;
- `data_root_status`;
- `data_root_path` при настроенной Data;
- `source_location_profile`;
- `content_runtime_profile`.

Runtime composition раскрывается через `runtime_packages`, а не `package_mounts`.

Provided system directories:

- `install_root_system_dir`;
- `user_private_system_dir`.

Refs:

- `health_snapshot_ref`;
- `user_state_ref`;
- `session_ref`;
- `active_session_ref`;
- `runtime_state_ref`.

Старые поля `primary_root`, `primary_source_location_profile`, `primary_content_runtime_profile`, `user_local_system_dir`, `cleanup_registry_ref` и `package_mounts` не поддерживаются.

## 6. Data

Connector фиксирует только:

```text
data_profile = data_enabled
```

Способ размещения и привязки Data выбирается в Studio. Strategy Box использует `workspace.data_root_path`, а при его отсутствии работает в degraded mode согласно Activation Context и session state.

## 7. Проверочный сценарий

1. Studio проверяет `stratbox-windows` и признаёт его manifest authority.
2. Studio сопоставляет `stratbox_core_source` с репозиторием `stratbox`.
3. Пользователь выбирает недостающие параметры `WorldDefinition`, включая Data binding.
4. AppDock фиксирует exact revisions обоих sources.
5. AppDock формирует два package и materialization document.
6. AppDock устанавливает `stratbox`, затем `stratbox-windows` в managed environment.
7. AppDock формирует Activation Context `3.0` с двумя `runtime_packages`.
8. Entrypoint проверяет runtime graph.
9. Сначала выполняется `--diagnose`, затем обычный запуск surface `desktop`.


## 8. Cross-repository contract check

Для проверки против конкретного checkout AppDock:

```bash
python scripts/check_appdock_contract.py --appdock-repository ../AppDock
```

Проверка использует реальный AppDock Connector parser, semantic admission и activation-target resolver. Она должна выполняться после изменений manifest или обновления контрактов AppDock.
