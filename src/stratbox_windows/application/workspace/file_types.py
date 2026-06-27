from __future__ import annotations

from pathlib import Path

_FILE_TYPE_MAP: dict[str, tuple[str, str]] = {
    '.xlsx': ('excel', 'Лист Excel'),
    '.xls': ('excel', 'Лист Excel'),
    '.csv': ('csv', 'CSV-файл'),
    '.json': ('json', 'JSON-файл'),
    '.txt': ('text', 'Текстовый файл'),
    '.log': ('text', 'Текстовый файл'),
    '.md': ('text', 'Текстовый файл'),
    '.pdf': ('pdf', 'PDF-документ'),
    '.png': ('image', 'Изображение'),
    '.jpg': ('image', 'Изображение'),
    '.jpeg': ('image', 'Изображение'),
    '.bmp': ('image', 'Изображение'),
    '.webp': ('image', 'Изображение'),
    '.svg': ('image', 'Изображение'),
    '.zip': ('archive', 'Архив'),
    '.7z': ('archive', 'Архив'),
    '.rar': ('archive', 'Архив'),
    '.tar': ('archive', 'Архив'),
    '.gz': ('archive', 'Архив'),
}


def resolve_file_type(path: Path) -> tuple[str, str]:
    extension = path.suffix.lower()
    return _FILE_TYPE_MAP.get(extension, ('file', 'Файл'))
