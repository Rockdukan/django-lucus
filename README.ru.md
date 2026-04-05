# Lucus

[English](README.md)

Lucus — пакет для Django, который переоформляет `django.contrib.admin`: свой `base.html`, CSS вёрстки и один общий лист админки (`lucus/css/lucus-admin.css`) вместо подключения стандартных `admin/css/`. Палитра и режим отображения (светлая, тёмная или как в системе) выбираются в шапке и сохраняются для каждого пользователя в модели `LucusAdminUiPreference`. Главная страница `/admin/` поддерживает настраиваемый многоколоночный дашборд.

Боковая панель навигации Django в админке отключена. На страницах списка объектов и редактирования записи основные действия закреплены у нижней границы окна просмотра, чтобы оставаться доступными при прокрутке.

![Главная админки — тема Dune, светлое оформление, фон на весь экран](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_1.jpg)

*Индекс: многоколоночный дашборд с карточками приложений (примеры: Education, Logistics, Support и др.), в шапке — палитра, оформление, сайт, язык, пользователь.*

![Список объектов — тема Slate (модель Instructors)](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_2.jpg)

*Changelist: «хлебные крошки», поиск, массовые действия, таблица результатов, фильтры справа.*

![Форма объекта — тема Dracula, тёмное оформление](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_3.jpg)

*Форма изменения: поля, закреплённая нижняя панель (сохранение и удаление). На кадре — тёмный режим; палитра и режим задаются настройками пользователя.*

## Требования

- Python 3.10+
- Django `>=5.2,<7` (`pyproject.toml`)

## Установка

```bash
pip install django-lucus
```

На PyPI пакет называется **django-lucus**, в коде приложение подключается как `lucus`.

## Подключение

```python
INSTALLED_APPS = [
    # ...
    "lucus",
    "django.contrib.admin",
]
```

```bash
python manage.py migrate lucus_admin
```

В продакшене выполните `collectstatic`, чтобы статика админки отдавалась так же, как остальные файлы.

## Настройки

| Настройка | Тип | По умолчанию | Назначение |
|-----------|-----|--------------|------------|
| `SITE_NAME` | `str` | `"Site"` | Шаблон заголовка / `site_title` |
| `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` | `str` | `"Administration — {site}"` | `admin.site.site_header` = `.format(site=SITE_NAME)`; безопасно только `{site}`, остальные `{}` экранировать |
| `LUCUS_ADMIN_SITE_TITLE_USE_SITE_NAME` | `bool` | `True` | При `True`: `admin.site.site_title` = `SITE_NAME` |
| `LUCUS_ADMIN_BACKGROUND_IMAGE` | `str` / `Path` | `""` | Фон на весь экран: `http(s)://`, `//`, путь сайта `/…` или static (без `..`) |
| `LUCUS_ADMIN_BACKGROUND_SCRIM_OPACITY` | `float` | `0.88` | Непрозрачность цветной подложки поверх картинки, `0.0`…`1.0` |
| `LUCUS_ADMIN_LANGUAGE_SELECTOR` | `bool` | *(авто)* | `False` — скрыть выбор языка в шапке. Иначе показ только при `USE_I18N`, `len(LANGUAGES) > 1`, `LocaleMiddleware`, URL `set_language` |
| `LUCUS_ADMIN_SITE_SELECTOR` | `bool` | *(авто)* | `False` — скрыть переключатель сайтов. Иначе при `sites` и ≥2 `Site` |
| `LUCUS_UI` | `dict` | `{}` | См. ниже |
| `LUCUS_EXTRA_STATIC_CSS` | `str` / `list` / `tuple` | `()` | Доп. CSS после палитры; без `..` и без ведущего `/` |
| `LUCUS_EMPTY_VALUE_DISPLAY_WRAP` | `bool` | `True` | Оборачивать пустые ячейки changelist в `lucus-admin-empty` |
| `LUCUS_EMPTY_VALUE_PLACEHOLDER` | `str` | `"—"` | Текст `empty_value_display` |
| `LUCUS_ACTIONS_ON_BOTTOM` | `bool` | `True` | `ModelAdmin.actions_on_bottom` на классе |
| `LUCUS_ACTIONS_ON_TOP` | `bool` | `True` | `ModelAdmin.actions_on_top` на классе |
| `LUCUS_DASHBOARD` | `list` / `None` | `None` | Дашборд; `None` — встроенная групповая сетка |
| `LUCUS_DASHBOARD_APPEND_UNCOVERED` | `bool` | `True` | Групповой режим: непокрытые приложения в последнюю колонку |

**Палитра и оформление** не задаются в `settings`: значения хранятся в `LucusAdminUiPreference`. Встроенные слаги: `olivia`, `grey`, `slate`, `dune`, `midnight`, `nord`, `dracula`, `github`, `catppuccin`, `tokyo` — файлы `lucus/static/lucus/css/<slug>.css`. Данные для шаблонов добавляет `lucus.theme.lucus_admin_extra_context` через `admin.site.each_context`.

### `LUCUS_UI`

| Ключ | По умолчанию | Назначение |
|------|----------------|------------|
| `help_as_icon` | `True` | `help_text` поля за `?` / `<details>` |
| `high_contrast_toggle` | `False` | Пункт меню «High contrast» (`localStorage`, `data-lucus-contrast` на `<html>`) |

```python
LUCUS_UI = {
    "help_as_icon": True,
    "high_contrast_toggle": False,
}
```

## `LUCUS_DASHBOARD`

Контекст: `lucus_dashboard_columns` из `get_dashboard_for_request`. Ссылка секции: `{"label", "url"}` или `{"label", "admin_urlname"}` (напр. `admin:app_model_changelist`). Секция без рабочих ссылок не показывается.

**Режим layout:** `[{ "column"?: 1–4, "classes"?: str, "sections": [{ "title", "links": [...] }] }, …]`. Одинаковый `column` — объединение секций; `classes` из первого словаря.

**Режим групп:** `[{ "column", "title", "links"?: [...], "app_labels"?: set|list|tuple|frozenset }, …]`. Сначала `links`, затем модели из `app_labels`; дубликаты URL убираются. Для `list`/`tuple` порядок приложений как в списке; для `set` — как в `get_app_list`.

`LUCUS_DASHBOARD_APPEND_UNCOVERED`: `True` — остальные приложения в последнюю колонку; `False` — только заданные группы.

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

```python
LUCUS_DASHBOARD = [
    {"column": 1, "title": "Авторизация", "app_labels": {"auth"}},
]
```

```python
LUCUS_DASHBOARD = [
    {
        "column": 2,
        "title": "Auth",
        "links": [{"label": "Пользователи", "admin_urlname": "admin:auth_user_changelist"}],
        "app_labels": ("auth",),
    },
]
```

## Стили

Подключаются по порядку: `lucus/css/style.css`, `lucus/css/lucus-admin.css`, выбранная палитра `lucus/css/<slug>.css`, затем пути из `LUCUS_EXTRA_STATIC_CSS`. JavaScript виджетов, инлайнов и действий по-прежнему из `django.contrib.admin`.

Свою палитру можно добавить, положив в static файл `lucus/css/<slug>.css` и дописав пару `(slug, подпись)` в `lucus.theme.BUNDLED_COLOR_SCHEMES` в проекте.

## Модули

| Модуль | Назначение |
|--------|------------|
| `lucus.apps.LucusConfig` | `ready()`: `site_header` / `site_title`, подключение `each_context`, контекст дашборда, маршруты `lucus_save_ui` и `lucus_save_site`, `enable_nav_sidebar = False`, `empty_value_display`, размещение действий `ModelAdmin` |
| `lucus.dashboard` | Разбор `LUCUS_DASHBOARD` в структуру колонок |
| `lucus.models` | `LucusAdminUiPreference` (палитра и оформление на пользователя) |
| `lucus.theme` | Встроенные схемы, `lucus_admin_extra_context(request)` |
| `lucus.views` | Обработчики POST для сохранения UI и выбора сайта |

Версия пакета: `lucus.__version__`.

Если используется переключатель сайтов в шапке и нужно, чтобы внутри `/admin/` объект `request.site` совпадал с выбором, зарегистрируйте `lucus.sites_panel.LucusAdminSiteMiddleware` сразу после `SessionMiddleware` (см. `lucus.sites_panel`).

Поддерживаемые версии Django указаны в `pyproject.toml` (ориентир — 5.2 и совместимая линия 6.x).
