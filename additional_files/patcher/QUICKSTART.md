# Quick Start: Variant Code Patcher

## Установка

Убедитесь что установлен PyYAML:
```bash
pip install PyYAML
```

## Базовое использование

### 1. Применение патча к файлу

```bash
python3 additional_files/patcher/apply_patch.py <file> <patch.yml>
```

### 2. Применение патча к каталогу

```bash
# Все файлы в каталоге
python3 additional_files/patcher/apply_patch.py <dir> <patch.yml>

# Рекурсивно по подкаталогам
python3 additional_files/patcher/apply_patch.py --recursive <dir> <patch.yml>

# Только файлы с определёнными расширениями
python3 additional_files/patcher/apply_patch.py --extensions .cpp .h <dir> <patch.yml>
```

### 3. Бекапы с ID и откат

```bash
# Применить патч с тегом бекапа
python3 additional_files/patcher/apply_patch.py --backup inkhud_ru <file|dir> <patch.yml>

# Откатить по ID
python3 additional_files/patcher/apply_patch.py --rollback inkhud_ru <file|dir>

# Откатить последний (без ID)
python3 additional_files/patcher/apply_patch.py --rollback <file|dir>

# Откатить по ID и удалить бекапы
python3 additional_files/patcher/apply_patch.py --rollback inkhud_ru --cleanup <file|dir>
```

### 4. Dry-run режим (тестирование без изменений)

```bash
python3 additional_files/patcher/apply_patch.py --dry-run <file|dir> <patch.yml>
```

### 5. Сохранение JSON отчета

```bash
# В STDOUT
python3 additional_files/patcher/apply_patch.py <file|dir> <patch.yml> > report.json

# В файл через параметр
python3 additional_files/patcher/apply_patch.py --json-output report.json <file|dir> <patch.yml>
```

### 6. CI/CD проверка (ошибка если нет изменений)

```bash
python3 additional_files/patcher/apply_patch.py --error-no-changes <file|dir> <patch.yml>
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

  - type: replace
    description: "Замена со строгим числом совпадений"
    count: 3
    search: "строго_3_раза"
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
# Применить патч с тегом бекапа
python3 additional_files/patcher/apply_patch.py \
  --backup inkhud_ru \
  path/to/variants/heltec_wireless_paper \
  additional_files/patcher/patches/INKHUD_RU.yml

# Откатить если что-то пошло не так
python3 additional_files/patcher/apply_patch.py --rollback inkhud_ru path/to/variants/heltec_wireless_paper
```

### Проверка числа замен (count)

Поле `count` — строгое ожидание числа совпадений. Если реальное число не совпадает — патч не применяется.

- Для **файла**: проверяется число совпадений в файле
- Для **каталога**: проверяется суммарное число совпадений по всем файлам

```yaml
patches:
  - type: replace
    count: 1                      # Ожидаем ровно 1 совпадение
    search: "FREESANS_12PT_WIN1252"
    replace: "FREESANS_12PT_WIN1251"
```

Если найдено 0 или 2+ совпадений — ошибка `count_mismatch`, файлы не изменяются.

## Коды возврата

- `0`: Успех
- `1`: Ошибка (невалидный YAML, файл не найден)
- `2`: Нет изменений (с --error-no-changes)
- `3`: Ошибка в патче (regex, pattern not found, count mismatch)
- `4`: Ошибка файловой системы

## Все параметры CLI

```
apply_patch.py [-h] [--dry-run] [--error-no-changes] [--recursive]
               [--extensions [EXTENSIONS ...]] [--json-output [JSON_OUTPUT]]
               [--rollback [ROLLBACK]] [--backup BACKUP] [--cleanup]
               file [patch_file]

Позиционные:
  file                  Файл или каталог
  patch_file            YAML патч-файл (не нужен с --rollback)

Опции:
  --dry-run             Показать изменения без модификации файлов
  --error-no-changes    Код 2 если нет изменений (CI/CD)
  --recursive           Рекурсивный обход каталога
  --extensions .cpp .h  Фильтр по расширениям (каталог)
  --json-output FILE    Сохранить JSON отчёт в файл
  --backup ID           Тег бекапа для целевого отката
  --rollback [ID]       Откат. С ID — по конкретному тегу, без — последний
  --cleanup             Удалить бекапы после восстановления
```

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
