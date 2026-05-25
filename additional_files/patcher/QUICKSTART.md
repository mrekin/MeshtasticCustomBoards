# Quick Start: Variant Code Patcher

## Установка

Убедитесь что установлен PyYAML:
```bash
pip install PyYAML
```

## Базовое использование

### 1. Применение патча

```bash
cd /path/to/MeshtasticCustomBoards
python3 additional_files/patcher/apply_patch.py <file> <patch.yml>
```

**Пример:**
```bash
python3 additional_files/patcher/apply_patch.py \
  firmware/variants/esp32s3/heltec_vmaster_e213_ru/nicheGraphics.h \
  additional_files/patcher/patches/INKHUD_RU.yml
```

### 2. Dry-run режим (тестирование без изменений)

```bash
python3 additional_files/patcher/apply_patch.py --dry-run <file> <patch.yml>
```

### 3. Сохранение JSON отчета

```bash
# В файл
python3 additional_files/patcher/apply_patch.py <file> <patch.yml> > report.json

# С параметром
python3 additional_files/patcher/apply_patch.py --json-output report.json <file> <patch.yml>
```

### 4. CI/CD проверка (ошибка если нет изменений)

```bash
python3 additional_files/patcher/apply_patch.py --error-no-changes <file> <patch.yml>
# Exit code 2 если патч не сделал изменений
```

## Создание собственных патчей

Создайте YAML файл со следующей структурой:

```yaml
description: "Описание патча"

patches:
  - type: replace
    description: "Замена подстроки"
    search: "старое_значение"
    replace: "новое_значение"

  - type: regex_replace
    description: "Замена по регулярному выражению"
    pattern: "define VERSION (?P<major>\\d+)\\.(?P<minor>\\d+)"
    replacement: "define VERSION \\g<major>.\\g<minor>"

  - type: line_insert
    description: "Вставка строки"
    insert_after: "#include \"base.h\""
    line: "#include \"custom.h\""
```

Подробнее см. `additional_files/patcher/patches/README.md`

## Практические примеры

### Русификация InkHUD

```bash
# Применить патч для замены WIN1252 на WIN1251
python3 additional_files/patcher/apply_patch.py \
  path/to/nicheGraphics.h \
  additional_files/patcher/patches/INKHUD_RU.yml
```

### Изменение версии

```bash
# Создать патч version.yml:
# description: "Update version"
# patches:
#   - type: regex_replace
#     pattern: "VERSION \\d+\\.\\d+"
#     replacement: "VERSION 2.0"

python3 additional_files/patcher/apply_patch.py \
  path/to/config.h \
  version.yml
```

## Коды возврата

- `0`: Успех
- `1`: Ошибка (невалидный YAML, файл не найден)
- `2`: Нет изменений (с --error-no-changes)
- `3`: Ошибка в патче (regex, pattern not found)
- `4`: Ошибка файловой системы

## Troubleshooting

### PyYAML не установлен
```bash
pip install PyYAML
```

### Файл не найден
Используйте абсолютные пути или запускайте из корня проекта.

### Патч не применяется
Используйте `--dry-run` для проверки что изменится.

### Нужна помощь
```bash
python3 additional_files/patcher/apply_patch.py --help
```

## Документация

- Patches README: `additional_files/patcher/patches/README.md`
