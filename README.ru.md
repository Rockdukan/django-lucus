# Lucus (Django Admin)

**Другие языки:** [English](README.md)

**Lucus** переоформляет **django.contrib.admin**: свой базовый шаблон, статика только из `lucus/static` (в т.ч. один файл **`lucus/css/lucus-admin.css`** вместо подключения `django.contrib.admin` CSS), выбор палитры и оформления **по пользователю** (и cookie для экрана входа), дашборд на `/admin/`. Боковая панель Django отключена; кнопки сохранения на change-form и блок действий changelist — **у низа видимой области окна**.

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

После обновления выполните миграции (модель предпочтений темы):

```bash
python manage.py migrate lucus_admin
```

## Справочник настроек

| Настройка | Тип | По умолчанию | Описание |
|-----------|-----|--------------|----------|
| `SITE_NAME` | `str` | `"Site"` | Подстановка в `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` и при `LUCUS_ADMIN_SITE_TITLE_USE_SITE_NAME` |
| `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` | `str` | `"Administration — {site}"` | `str.format(site=SITE_NAME)` для `admin.site.site_header`. В шаблоне безопасно использовать только `{site}` (остальные фигурные скобки нужно экранировать). |
| `LUCUS_ADMIN_SITE_TITLE_USE_SITE_NAME` | `bool` | `True` | Если `True`, `admin.site.site_title` = `SITE_NAME` |
| *(нет)* | — | — | **Палитра** не задаётся в `settings`: в шапке сотрудник выбирает схему и оформление (светлая / тёмная / авто); сохраняется в **`LucusAdminUiPreference`**. Встроенные: `olivia`, `grey`, `slate`, `dune`, `midnight`. |
| `LUCUS_UI` | `dict` | см. ниже | `help_as_icon`, `high_contrast_toggle` (по умолчанию `True`). Панель сохранения на change-form и блок действий changelist — у **низа окна** (viewport). |
| `LUCUS_EXTRA_STATIC_CSS` | `str` \| `list` \| `tuple` | `()` | Доп. CSS относительно корней staticfiles, после схемы. Запрещены `..` и путь с начальным `/`. |
| `LUCUS_EMPTY_VALUE_DISPLAY_WRAP` | `bool` | `True` | Оборачивать пустые ячейки changelist в `<span class="lucus-admin-empty">` |
| `LUCUS_EMPTY_VALUE_PLACEHOLDER` | `str` | `"—"` | Текст для `empty_value_display` |
| `LUCUS_ACTIONS_ON_BOTTOM` | `bool` | `True` | Глобально для процесса: **`ModelAdmin.actions_on_bottom = True` на классе** |
| `LUCUS_DASHBOARD` | `list` \| `None` | `None` | Конфиг дашборда (см. [Дашборд](#dashboard-ru)); если не задан — группы по умолчанию |
| `LUCUS_DASHBOARD_APPEND_UNCOVERED` | `bool` | `True` | В **групповом** режиме: выносить непокрытые приложения в **последнюю** колонку |

Контекст темы: `lucus.theme.lucus_admin_extra_context(request)`, подмешивается в `admin.site.each_context`.

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

## Шаблоны и статика

Базовый шаблон — свой. Порядок: `style.css` → **`lucus-admin.css`** (единый слой админки в пакете, без `<link>` на `admin/css/`) → палитра (`<slug>.css`) → `LUCUS_EXTRA_STATIC_CSS`.

JavaScript виджетов админки по-прежнему из `django.contrib.admin` (`admin/js/…`).

**Встроенные палитры:**

| Файл | Назначение |
|------|------------|
| `style.css` | Масштаб, сетка, UI |
| `olivia.css` | Зелёно-серая палитра по умолчанию |
| `grey.css` | Сине-серая |
| `slate.css` | «Шифер» |
| `dune.css` | Песочные акценты |
| `midnight.css` | Тёмная пара к светлой |

## Структура пакета

| Модуль | Назначение |
|--------|------------|
| `lucus.apps.LucusConfig` | `ready()`: заголовки, `each_context`, дашборд, URL сохранения темы, `enable_nav_sidebar = False`, `empty_value_display`, `actions_on_bottom` |
| `lucus.dashboard` | Нормализация конфигурации, колонки, ссылки |
| `lucus.models` | `LucusAdminUiPreference` |
| `lucus.theme` | Список палитр, `lucus_admin_extra_context(request)` |
| `lucus.views` | Сохранение предпочтений темы (POST) |

Версия: `lucus.__version__` (при релизе синхронизируйте с метаданными пакета).

## Совместимость

Lucus ориентирован на **Django 5.2+** и линию 5.x / 6.x согласно `pyproject.toml`.
