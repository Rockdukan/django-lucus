# Lucus (Django Admin)

**Другие языки:** [English](README.md)

**Lucus** переоформляет **django.contrib.admin**: отдельный базовый шаблон админки, многослойные стили (вёрстка + цветовые схемы), опциональная перегруппировка бокового меню и настраиваемый много колоночный дашборд на `/admin/`.

![Lucus dashboard](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_1.jpg)
![Lucus dashboard](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_2.jpg)
![Lucus dashboard](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_3.jpg)

## Требования

- Python 3.10+
- Django 5.2+ (в метаданных пакета: `django>=5.2,<7`)

## Установка

```bash
pip install django-lucus
```

Имя импорта: `lucus`. Имя дистрибутива на PyPI: **django-lucus**.

## Быстрый старт

Подключите **Lucus перед** `django.contrib.admin`, чтобы подхватились шаблоны Lucus:

```python
INSTALLED_APPS = [
    # ...
    "lucus",
    "django.contrib.admin",
    # ...
]
```

Шаблоны и статика идут в составе пакета; в продакшене используйте `collectstatic`.

## Справочник настроек

| Настройка | Тип | По умолчанию | Описание |
|-----------|-----|--------------|----------|
| `SITE_NAME` | `str` | `"Site"` | Подстановка в `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` и при `LUCUS_ADMIN_SITE_TITLE_USE_SITE_NAME` |
| `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` | `str` | `"Administration — {site}"` | `str.format(site=SITE_NAME)` для `admin.site.site_header`. В шаблоне безопасно использовать только `{site}` (остальные фигурные скобки нужно экранировать). |
| `LUCUS_ADMIN_SITE_TITLE_USE_SITE_NAME` | `bool` | `True` | Если `True`, `admin.site.site_title` = `SITE_NAME` |
| `LUCUS_COLOR_SCHEME` | `str` | `"olivia"` | Имя файла `static/lucus/css/<имя>.css`; допустимы `a-z`, `0-9`, `_`, `-`, длина 1–64. При невалидном значении — `olivia`. |
| `LUCUS_EXTRA_STATIC_CSS` | `str` \| `list` \| `tuple` | `()` | Доп. CSS относительно корней staticfiles, после схемы. Запрещены `..` и путь с начальным `/`. |
| `LUCUS_EMPTY_VALUE_DISPLAY_WRAP` | `bool` | `True` | Оборачивать пустые ячейки changelist в `<span class="lucus-admin-empty">` |
| `LUCUS_EMPTY_VALUE_PLACEHOLDER` | `str` | `"—"` | Текст для `empty_value_display` |
| `LUCUS_ACTIONS_ON_BOTTOM` | `bool` | `True` | Глобально для процесса: **`ModelAdmin.actions_on_bottom = True` на классе** |
| `LUCUS_SIDEBAR_REORGANIZE` | `bool` | `True` | Обёртка `admin.site.get_app_list` с `reorganize_admin_app_list` |
| `LUCUS_DASHBOARD` | `list` \| `None` | `None` | Конфиг дашборда (см. [Дашборд](#dashboard-ru)); если не задан — группы по умолчанию |
| `LUCUS_DASHBOARD_APPEND_UNCOVERED` | `bool` | `True` | В **групповом** режиме: выносить непокрытые приложения в **последнюю** колонку |

Контекст темы: `lucus.theme.lucus_admin_extra_context()`, подмешивается в `admin.site.each_context`.

<a id="dashboard-ru"></a>

## Дашборд: `LUCUS_DASHBOARD`

Распознаются два формата (`lucus.dashboard`: `looks_like_dashboard_layout`, `looks_like_groups_config`).

Контекст шаблона: **`lucus_dashboard_columns`** — `tuple[DashboardColumn, ...]` из `get_dashboard_for_request(request)`.

Ссылка в секции задаётся так:

- `url` — явный URL  
- `admin_urlname` — например `admin:app_model_changelist` (через `reverse()`)

Секция показывается только если разрешилась хотя бы одна ссылка.

### Режим 1: колонки layout

Список словарей с `classes` и/или `sections`. Необязательный **`column`** в диапазоне `1..4`: несколько словарей с одним и тем же `column` **объединяются** (секции подряд; `classes` берутся из первого словаря этой колонки). Номер колонки ограничен **1–4**.

### Режим 2: группы по колонкам

Список словарей с полями:

- **`column`** (от 1, минимум 1; сетка по сути **1–4**)
- **`title`** — заголовок карточки
- **`links`** — необязательно, список `{"label", "admin_urlname"|"url"}`
- **`app_labels`** — необязательно, `set`, `frozenset`, `list` или `tuple` строк `app_label`

Правила:

- В группе сначала идут явные `links` (по порядку), затем модели из `app_labels`. **Дубликаты URL отбрасываются.**
- Для **`list` / `tuple`** порядок приложений как в списке; порядок моделей как в админке.
- Для **`set` / `frozenset`** порядок приложений как в `get_app_list`.

**Непокрытые приложения:** при `LUCUS_DASHBOARD_APPEND_UNCOVERED = True` в последнюю колонку добавляются приложения вне множества «покрытых». В покрытие входят все `app_label` из групп и приложения, выведенные из успешно разрешённых `admin_urlname` в `links` (шаблон `admin:<app>_<model>_changelist`, сопоставление `app_label` — сначала более длинные совпадения). Чтобы **не** добавлять хвост из остальных приложений, задайте **`False`**.

### Примеры

**Layout с явными колонками:**

```python
LUCUS_DASHBOARD = [
    {
        "column": 1,
        "classes": "lucus-dashboard__col lucus-col lucus-col-3 lucus-col-md-6 lucus-col-sm-12",
        "sections": [
            {
                "title": "Обучение",
                "links": [
                    {"label": "Инструкторы", "admin_urlname": "admin:academy_instructor_changelist"},
                    {"label": "Курсы", "url": "/admin/academy/course/"},
                ],
            },
        ],
    },
]
```

**Группы с `app_labels`:**

```python
LUCUS_DASHBOARD = [
    {"column": 1, "title": "Авторизация", "app_labels": {"auth"}},
]
```

**Смешанно `links` + `app_labels`:**

```python
LUCUS_DASHBOARD = [
    {
        "column": 2,
        "title": "Auth",
        "links": [
            {"label": "Пользователи", "admin_urlname": "admin:auth_user_changelist"},
        ],
        "app_labels": ("auth",),
    },
]
```

## Боковое меню

При `LUCUS_SIDEBAR_REORGANIZE = True` вызывается `lucus.sidebar.patch_admin_get_app_list()`. Для полного списка (`app_label is None`) результат проходит через `reorganize_admin_app_list`: модели из ряда сторонних приложений сливаются в целевые (например redirects/constance/solo → sites), часть заголовков секций переводится. Патч идемпотентен.

## Шаблоны и статика

`templates/admin/base.html` **не** наследует стандартный `admin/base.html`; подключаются те же базовые CSS/JS админки Django плюс ресурсы Lucus.

Порядок в `extrastyle`:

1. `lucus/css/style.css` — сетка и компоненты (CSS-переменные).
2. Файл схемы: `lucus_scheme_stylesheet` → `lucus/css/<LUCUS_COLOR_SCHEME>.css` (в шаблоне запасной вариант — `lucus/css/olivia.css`).
3. Пути из `lucus_extra_stylesheets` (`LUCUS_EXTRA_STATIC_CSS`).

Встроенные схемы:

| Файл | Назначение |
|------|------------|
| `style.css` | Масштаб, сетка, UI; акценты через `var(--lucus-accent)` и т.д. |
| `olivia.css` | Светлая зелёно-серая палитра по умолчанию |
| `grey.css` | Альтернатива: сине-серая палитра |

Своя схема: добавьте `static/lucus/css/<slug>.css` в проект и укажите `LUCUS_COLOR_SCHEME = "<slug>"`.

## Структура пакета

| Модуль | Назначение |
|--------|------------|
| `lucus.apps.LucusConfig` | `ready()`: заголовки, `each_context`, дашборд, тема, сайдбар, `empty_value_display`, `actions_on_bottom` |
| `lucus.dashboard` | Нормализация конфигурации, колонки, ссылки |
| `lucus.sidebar` | `reorganize_admin_app_list`, `patch_admin_get_app_list` |
| `lucus.theme` | `lucus_admin_extra_context` для шаблонов |

Версия: `lucus.__version__` (при релизе синхронизируйте с метаданными пакета).

## Совместимость

Lucus ориентирован на **Django 5.2+** и линию 5.x / 6.x согласно `pyproject.toml`.
