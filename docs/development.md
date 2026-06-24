# Локальная разработка

## Ожидаемая структура каталогов

```text
Alta Veritas/
  stratbox/
  stratbox-windows/
  stratbox-plugin/
```

`stratbox-windows` живёт в связке с внешним `stratbox`. Для локальной разработки удобнее всего ставить оба репозитория в одно виртуальное окружение.

## Базовая установка

В PowerShell:

```powershell
cd "C:\Users\merku\Documents\Projects\Alta Veritas\stratbox-windows"

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel
python -m pip install -e "..\stratbox"
python -m pip install -e .
python -m pip install -e "..\stratbox-plugin"
python -m pip install -e ".[test]"
```

## Локальный запуск

```powershell
python -m stratbox_windows --standalone-dev-root ".\.tmp\dev-workspace"
```

Диагностика:

```powershell
python -m stratbox_windows --standalone-dev-root ".\.tmp\dev-workspace" --diagnose
```

## Минимальные проверки

```powershell
python scripts/check_release_integrity.py
python scripts/check_internal_imports.py
python -m pytest
```

## Что не должно попадать в Git

- `.venv/`
- `.venv-build/`
- `venv/`
- `.tmp/`
- `build/`
- `dist/`
- `__pycache__/`
- `*.egg-info/`

Если что-то из этого уже попало в историю, `.gitignore` сам по себе не поможет: нужно убрать файлы из Git-индекса или, если репозиторий новый, пересоздать локальную git-историю.
