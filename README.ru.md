# Lucus (оформление Django admin)

[English](README.md)

Свой `base.html`, статика Lucus (`lucus/css/style.css`, `lucus-admin.css`), палитра и светлая/тёмная/авто на пользователя (`LucusAdminUiPreference`), настраиваемый дашборд `/admin/`. Боковая навигация Django отключена; действия changelist и панель сохранения change-form закреплены у низа viewport.

![Lucus](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_1.jpg)
![Lucus](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_2.jpg)
![Lucus](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_3.jpg)

## Требования

- Python 3.10+
- Django `>=5.2,<7` (`pyproject.toml`)

## Установка

```bash
pip install django-lucus
```

Импорт: `lucus`. PyPI: **django-lucus**.

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

Продакшен: `collectstatic`.

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

**Палитра и тема:** не в `settings`. В БД: `LucusAdminUiPreference`. Слуги: `olivia`, `grey`, `slate`, `dune`, `midnight`, `nord`, `dracula`, `github`, `catppuccin`, `tokyo` → `lucus/static/lucus/css/<slug>.css`. Контекст: `lucus.theme.lucus_admin_extra_context` в `admin.site.each_context`.

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

## Статика

Порядок: `lucus/css/style.css` → `lucus/css/lucus-admin.css` → `lucus/css/<slug>.css` → `LUCUS_EXTRA_STATIC_CSS`. JS виджетов — из `django.contrib.admin`.

Своя палитра: файл `lucus/css/<slug>.css` в static + дополнение `lucus.theme.BUNDLED_COLOR_SCHEMES` в проекте.

## Пакет

- `lucus.apps.LucusConfig` — `ready()`: заголовки, `each_context`, дашборд, URL `lucus_save_ui` / `lucus_save_site`, `enable_nav_sidebar = False`, пустые значения, флаги actions
- `lucus.dashboard` — конфиг → колонки
- `lucus.models` — `LucusAdminUiPreference`
- `lucus.theme` — палитры, `lucus_admin_extra_context`
- `lucus.views` — POST сохранения UI / сайта

Версия: `lucus.__version__`.

**Панель сайтов:** чтобы `request.site` в админке совпадал с выбором в шапке, подключите `lucus.sites_panel.LucusAdminSiteMiddleware` после `SessionMiddleware` (`lucus.sites_panel`).

**Совместимость:** Django 5.2+ (`pyproject.toml`).
