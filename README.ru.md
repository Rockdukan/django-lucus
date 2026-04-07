# django-lucus

[English](README.md)

**django-lucus** — кастомная тема оформления для встроенной админки Django (`django.contrib.admin`): другой внешний вид страниц, набор цветовых схем, на главной `/admin/` — всегда многоколоночный дашборд (не «плоский» список приложений как в стоке). Как именно разложены колонки и ссылки, задаётся **`LUCUS_DASHBOARD`**; если настройку не задавать, Lucus сам строит колонки из ваших зарегистрированных приложений. В проект добавляется приложение **`lucus`**. Адрес админки в браузере тот же, что был до подключения (часто **`/admin/`** — зависит от вашего `urls.py`).

- **Оформление:** подменяются шаблоны «оболочки» админки; стили подключаются по цепочке: `lucus/css/style.css` → `lucus-admin.css` → файл выбранной палитры `lucus/css/schemes/<slug>.css`.
- **Навигация:** встроенная боковая панель списка приложений Django в админке отключена (`AdminSite.enable_nav_sidebar = False`).
- **Для каждого пользователя:** выбранная цветовая схема и режим «светло / тёмно / как в системе» хранятся в модели **`LucusAdminUiPreference`**.
- **Меню на внутренних страницах:** если **`LUCUS_SIDE_DASHBOARD_NAV`** включён (по умолчанию да), на страницах админки кроме главной показывается боковое или выезжающее меню в том же духе, что и дашборд на главной.
- **Списки объектов и формы редактирования:** по умолчанию блок массовых действий показывается и над таблицей, и под ней; на форме объекта кнопки сохранения и удаления могут быть закреплены внизу экрана. Глобальные переключатели — в настройках **`LUCUS_ACTIONS_ON_TOP`** и **`LUCUS_ACTIONS_ON_BOTTOM`** (таблица ниже); для отдельных моделей всё это можно изменить в своём классе админки (**`ModelAdmin`**), как в обычном Django.

![Главная админки — палитра Dune, светлое оформление, фон на весь экран](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_1.jpg)

*Индекс: многоколоночный `LUCUS_DASHBOARD`; шапка — палитра, оформление, опционально сайт / язык, меню пользователя.*

![Список объектов — палитра Slate (пример модели)](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_2.jpg)

*Changelist: крошки, тулбар (пагинация + поиск), массовые действия, таблица, блок фильтров.*

![Форма объекта — палитра Dracula, тёмное оформление](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_3.jpg)

*Форма изменения: филдсеты; нижняя панель действий. Палитра и режим — на пользователя (`LucusAdminUiPreference`).*

## Требования

- Python ≥ 3.10  
- Django: `>=5.2,<7` (`pyproject.toml`)

## Установка

```bash
pip install django-lucus
```

## Подключение

Добавьте **`lucus`** в `INSTALLED_APPS` и поставьте его **выше** `django.contrib.admin`:

```python
INSTALLED_APPS = [
    # ...
    "lucus",
    "django.contrib.admin",
]
```

Если в проекте есть другое приложение с **тем же путём шаблона**, что и в Lucus, **`lucus` должен стоять раньше него**. Иначе Django подставит чужой файл. Типичный пример — **Rosetta**: в пакете лежат `lucus/templates/rosetta/…`; если `rosetta` окажется выше в списке, тема Lucus на страницах Rosetta не применится.

Затем:

```bash
python manage.py migrate lucus
```

В продакшене выполните **`collectstatic`**, чтобы отдавались файлы из `lucus/static/`.

## Настройки

| Настройка | Тип | По умолчанию | Назначение |
|-----------|-----|--------------|------------|
| `SITE_NAME` | `str` | `"Site"` | `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` / `site_title` |
| `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` | `str` | `"Administration — {site}"` | `admin.site.site_header` = `.format(site=SITE_NAME)`; только `{site}` или экранировать прочие `{}` |
| `LUCUS_ADMIN_SITE_TITLE_USE_SITE_NAME` | `bool` | `True` | При `True`: `admin.site.site_title` = `SITE_NAME` |
| `LUCUS_ADMIN_BACKGROUND_IMAGE` | `str` / `Path` | `""` | Фон: `http(s)://`, `//`, путь `/…` или static (без `..`) |
| `LUCUS_ADMIN_BACKGROUND_SCRIM_OPACITY` | `float` | `0.88` | Подложка поверх изображения, `0.0`…`1.0` |
| `LUCUS_ADMIN_LANGUAGE_SELECTOR` | `bool` | *(авто)* | `False` — скрыть `<select>` языка. Иначе при `USE_I18N`, `len(LANGUAGES) > 1`, `LocaleMiddleware`, URL `set_language` |
| `LUCUS_ADMIN_SITE_SELECTOR` | `bool` | *(авто)* | `False` — скрыть переключатель сайтов; иначе при `sites` и ≥2 `Site` |
| `LUCUS_ADMIN_SITES` | `AdminSite` / `list` / `tuple` | `None` | Экземпляры `AdminSite` для патча (`each_context`, `get_urls`, заголовки, …). По умолчанию только `django.contrib.admin.site`. Пример: `LUCUS_ADMIN_SITES = (admin.site, my_site)`. Формы в `base.html` — `{% url 'admin:lucus_save_ui' %}`; другой namespace может потребовать свой шаблон. |
| `LUCUS_STAFF_THEME_PATH_PREFIXES` | `tuple` / `list` / `str` | *см. ниже* | Staff: подмешивать `each_context` на префиксах URL (шаблоны админки без `admin_view`). По умолчанию: `/logs/`, `/rosetta/`, `/explorer/`. `()` — отключить. |
| `LUCUS_UI` | `dict` | `{}` | См. ниже |
| `LUCUS_EXTRA_STATIC_CSS` | `str` / `list` / `tuple` | `()` | Доп. CSS после палитры; без `..` и без ведущего `/` |
| `LUCUS_EMPTY_VALUE_DISPLAY_WRAP` | `bool` | `True` | Пустые ячейки changelist — обёртка `lucus-admin-empty` |
| `LUCUS_EMPTY_VALUE_PLACEHOLDER` | `str` | `"—"` | Текст `empty_value_display` |
| `LUCUS_ACTIONS_ON_BOTTOM` | `bool` | `True` | Дефолт `ModelAdmin.actions_on_bottom` на уровне **класса**; переопределение в подклассе |
| `LUCUS_ACTIONS_ON_TOP` | `bool` | `True` | Дефолт `ModelAdmin.actions_on_top` на уровне **класса** |
| `LUCUS_DASHBOARD` | `list` / `None` | `None` | Дашборд; `None` — встроенная групповая сетка |
| `LUCUS_DASHBOARD_APPEND_UNCOVERED` | `bool` | `True` | Групповой режим: непокрытые приложения в последнюю колонку |
| `LUCUS_SIDE_DASHBOARD_NAV` | `bool` | `True` | Не индекс: сворачиваемое левое меню по колонкам `LUCUS_DASHBOARD`. Выкл. на индексе, в popup, без прав |

Палитра / оформление не в `settings`; в `LucusAdminUiPreference`. Слаги → `lucus/static/lucus/css/schemes/<slug>.css`. Контекст: `lucus.theme.lucus_admin_extra_context` через `admin.site.each_context`.

### `LUCUS_UI`

| Ключ | По умолчанию | Назначение |
|------|----------------|------------|
| `help_as_icon` | `True` | `help_text` за `?` / `<details>` |
| `high_contrast_toggle` | `False` | Меню пользователя: высокий контраст (`localStorage`, `data-lucus-contrast` на `<html>`) |
| `clean_input_types` | `False` | Подмена HTML5-типов у `<input>` на `text` (аналог `GRAPPELLI_CLEAN_INPUT_TYPES`) |

```python
LUCUS_UI = {
    "help_as_icon": True,
    "high_contrast_toggle": False,
    "clean_input_types": False,
}
```

## Табличные инлайны: сортировка и placeholder

1. **Перетаскивание строк** — `lucus.inlines.LucusSortableTabularInline` или `LucusSortableTabularInlineMixin` + `admin.TabularInline`. `sortable_field_name`, опционально `sortable_excludes`. Докстринг: `lucus/inlines.py`.
2. **Инлайн между fieldsets** — филдсет с `fields: ()`, в `classes` — `"placeholder"` и id обёртки инлайна (`<prefix>-group`, напр. `items_set-group`).

## Сторонние пакеты: CSS (`lucus/static/lucus/css/third_party/`)

Отдельных Python-зависимостей нет. Виды без `admin/base.html`: `LUCUS_STAFF_THEME_PATH_PREFIXES` + `lucus.context_processors.staff_integrations_theme`.

| Пакет | Файл | Подключение из |
|--------|------|----------------|
| django-constance | `lucus/css/third_party/constance.css` | `admin/base.html` |
| django-filer | `lucus/css/third_party/filer.css` | `admin/base.html` |
| django-parler | `lucus/css/third_party/parler.css` | `admin/base.html` |
| django-rosetta | `lucus/css/third_party/rosetta.css` | `rosetta/base.html` |
| django-log-viewer (совместимый) | `lucus/css/third_party/log_viewer.css` | `log_viewer/logfile_viewer.html` |

## `LUCUS_DASHBOARD`

Контекст: `lucus_dashboard_columns` из `get_dashboard_for_request`. Ссылка секции: `{"label", "url"}` или `{"label", "admin_urlname"}`. Секция без валидных ссылок не рендерится.

**Layout:** `[{ "column"?: 1–4, "classes"?: str, "sections": [{ "title", "links": [...] }] }, …]`. Один `column` — слияние секций; `classes` из первого словаря.

**Группы:** `[{ "column", "title", "links"?: [...], "app_labels"?: set|list|tuple|frozenset }, …]`. Сначала `links`, затем модели из `app_labels`; дубликаты URL удаляются. Для `list`/`tuple` порядок из списка; для `set` — как в `get_app_list`.

`LUCUS_DASHBOARD_APPEND_UNCOVERED`: `True` — остальные приложения в последнюю колонку; `False` — только заданные группы.

```python
LUCUS_DASHBOARD = [
    {
        "column": 1,
        "classes": "lucus-dashboard__col lucus-grid__col lucus-grid__col--3 lucus-grid__col--md-6 lucus-grid__col--sm-12 lucus-grid__col--xs-12",
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

## Порядок стилей

`lucus/css/style.css` → `lucus/css/lucus-admin.css` → `lucus/css/schemes/<slug>.css` → `LUCUS_EXTRA_STATIC_CSS`. JS виджетов / инлайнов / действий — из `django.contrib.admin`.

Своя палитра: static `lucus/css/<slug>.css` + расширение `lucus.theme.BUNDLED_COLOR_SCHEMES`.

Переопределён `admin/change_list_results.html`: `.text` затем `.sortoptions` внутри `.lucus-th-heading-inner` (вместо stock `float` у иконки сортировки).

## Тесты

```bash
pip install -r requirements-dev.txt
pytest
```

## Модули Python

| Модуль | Роль |
|--------|------|
| `lucus.apps.LucusConfig` | `ready()`: заголовки, `each_context`, дашборд, `lucus_save_ui` / `lucus_save_site`, `enable_nav_sidebar`, `empty_value_display`, дефолты действий `ModelAdmin` |
| `lucus.dashboard` | Нормализация `LUCUS_DASHBOARD` |
| `lucus.models` | `LucusAdminUiPreference` |
| `lucus.theme` | Схемы, `lucus_admin_extra_context` |
| `lucus.views` | POST: UI и сайт |

Если в шапке админки переключают сайт и нужно, чтобы **`request.site`** внутри запросов совпадал с этим выбором, подключите middleware **`lucus.sites_panel.LucusAdminSiteMiddleware`** сразу после **`SessionMiddleware`**. Как именно — описано в модуле **`lucus.sites_panel`**.

В репозитории для демонстрации интеграций есть приложение **`integration/`** и файл **`requirements-integration.txt`**; при необходимости: **`pip install -e ".[integration]"`**. Запуск демо-сайта — корневой **`manage.py`** с **`core.settings`**; часть сценариев зависит от установленного **`sorl.thumbnail`**.
