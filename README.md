# django-lucus

[Русский](README.ru.md)

**django-lucus** is a **custom theme** for Django’s built-in admin (`django.contrib.admin`): refreshed layout, bundled color schemes, and a **multi-column dashboard on `/admin/`** by default (not the stock flat app list). You shape columns and links with **`LUCUS_DASHBOARD`**; leave it unset and Lucus builds columns from your registered apps. Install the **`lucus`** app. Admin URLs stay the same as in your project (often **`/admin/`**, from `urls.py`).

- **Appearance:** Lucus replaces the admin “chrome” templates and loads CSS in order: `lucus/css/style.css` → `lucus-admin.css` → the selected palette file `lucus/css/schemes/<slug>.css`.
- **Navigation:** Django’s default admin app sidebar is turned off (`AdminSite.enable_nav_sidebar = False`).
- **Per signed-in user:** chosen palette and light / dark / system appearance are stored in **`LucusAdminUiPreference`**.
- **Nav inside the admin:** with **`LUCUS_SIDE_DASHBOARD_NAV`** (on by default), pages other than the index get a side or off-canvas menu in the same spirit as the home dashboard.
- **Lists and edit forms:** bulk-action bars default to both above and below the changelist; save / delete controls on object forms can sit in a fixed bar at the bottom of the viewport. Project-wide toggles are **`LUCUS_ACTIONS_ON_TOP`** and **`LUCUS_ACTIONS_ON_BOTTOM`** in the settings table below; each **`ModelAdmin`** subclass can still override behavior the usual Django way.

![Admin index — Dune palette, light appearance, full-page background](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_1.jpg)

*Index: multi-column `LUCUS_DASHBOARD` cards; header — palette, appearance, optional site / language selectors, user menu.*

![Changelist — Slate palette (example model)](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_2.jpg)

*Changelist: breadcrumbs, toolbar (pagination + search), bulk actions, results table, filter aside.*

![Change form — Dracula palette, dark appearance](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_3.jpg)

*Change form: fieldsets; fixed bottom action bar (save / delete). Palette and appearance are per-user (`LucusAdminUiPreference`).*

## Requirements

- Python ≥ 3.10  
- Django: `>=5.2,<7` (`pyproject.toml`)

## Install

```bash
pip install django-lucus
```

## Setup

Add **`lucus`** to `INSTALLED_APPS` and place it **above** `django.contrib.admin`:

```python
INSTALLED_APPS = [
    # ...
    "lucus",
    "django.contrib.admin",
]
```

If another installed app defines the **same template path** as Lucus, **`lucus` must come before it** in the list; otherwise Django will load the wrong template. A common case is **Rosetta**: Lucus ships `lucus/templates/rosetta/…`. If `rosetta` appears earlier, those pages won’t use Lucus’s wrappers.

Then:

```bash
python manage.py migrate lucus
```

In production, run **`collectstatic`** so `lucus/static/` is served.

## Settings

| Setting | Type | Default | Effect |
|---------|------|---------|--------|
| `SITE_NAME` | `str` | `"Site"` | `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` / `site_title` |
| `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` | `str` | `"Administration — {site}"` | `admin.site.site_header` = `.format(site=SITE_NAME)`; only `{site}` or escape other `{}` |
| `LUCUS_ADMIN_SITE_TITLE_USE_SITE_NAME` | `bool` | `True` | `admin.site.site_title` = `SITE_NAME` if true |
| `LUCUS_ADMIN_BACKGROUND_IMAGE` | `str` / `Path` | `""` | Full-page background: `http(s)://`, `//`, site path `/…`, or static path (no `..`) |
| `LUCUS_ADMIN_BACKGROUND_SCRIM_OPACITY` | `float` | `0.88` | Overlay on image, `0.0`…`1.0` |
| `LUCUS_ADMIN_LANGUAGE_SELECTOR` | `bool` | *(auto)* | `False` → hide header language `<select>`. Shown only if `USE_I18N`, `len(LANGUAGES) > 1`, `LocaleMiddleware`, `set_language` URL exists |
| `LUCUS_ADMIN_SITE_SELECTOR` | `bool` | *(auto)* | `False` → hide `django.contrib.sites` header switcher. Shown if sites app + ≥2 `Site` rows |
| `LUCUS_ADMIN_SITES` | `AdminSite` / `list` / `tuple` | `None` | `AdminSite` instances Lucus patches (`each_context`, `get_urls`, headers, …). Default: `django.contrib.admin.site` only. Example: `LUCUS_ADMIN_SITES = (admin.site, my_site)`. `base.html` forms use `{% url 'admin:lucus_save_ui' %}`; other namespaces may need template overrides. |
| `LUCUS_STAFF_THEME_PATH_PREFIXES` | `tuple` / `list` / `str` | *see below* | Staff: merge `AdminSite.each_context` on these URL prefixes (admin-like templates without `admin_view`). Default: `/logs/`, `/rosetta/`, `/explorer/`. `()` disables. |
| `LUCUS_UI` | `dict` | `{}` | See below |
| `LUCUS_EXTRA_STATIC_CSS` | `str` / `list` / `tuple` | `()` | Extra CSS after palette; no `..`, no leading `/` |
| `LUCUS_EMPTY_VALUE_DISPLAY_WRAP` | `bool` | `True` | Wrap empty changelist cells in `lucus-admin-empty` |
| `LUCUS_EMPTY_VALUE_PLACEHOLDER` | `str` | `"—"` | `empty_value_display` text |
| `LUCUS_ACTIONS_ON_BOTTOM` | `bool` | `True` | Default `ModelAdmin.actions_on_bottom` at **class** level; override per subclass |
| `LUCUS_ACTIONS_ON_TOP` | `bool` | `True` | Default `ModelAdmin.actions_on_top` at **class** level |
| `LUCUS_DASHBOARD` | `list` / `None` | `None` | Dashboard; `None` → built-in grouped layout |
| `LUCUS_DASHBOARD_APPEND_UNCOVERED` | `bool` | `True` | Grouped mode: append uncovered apps to last column |
| `LUCUS_SIDE_DASHBOARD_NAV` | `bool` | `True` | Non-index admin: collapsible left nav from `LUCUS_DASHBOARD` column order. Off on index, popups, no permission |

Palette / appearance: not in `settings`; stored per user. Slugs → `lucus/static/lucus/css/schemes/<slug>.css`. Context: `lucus.theme.lucus_admin_extra_context` via `admin.site.each_context`.

### `LUCUS_UI`

| Key | Default | Effect |
|-----|---------|--------|
| `help_as_icon` | `True` | Field `help_text` behind `?` / `<details>` |
| `high_contrast_toggle` | `False` | User menu: high contrast (`localStorage`, `data-lucus-contrast` on `<html>`) |
| `clean_input_types` | `False` | Map common HTML5 input types to `text` in admin (cf. Grappelli `GRAPPELLI_CLEAN_INPUT_TYPES`) |

```python
LUCUS_UI = {
    "help_as_icon": True,
    "high_contrast_toggle": False,
    "clean_input_types": False,
}
```

## Sortable tabular inlines & placeholder inlines

1. **Drag-sort rows** — `lucus.inlines.LucusSortableTabularInline` or `LucusSortableTabularInlineMixin` + `admin.TabularInline`. `sortable_field_name`, optional `sortable_excludes`. Docstring: `lucus/inlines.py`.
2. **Inline between fieldsets** — `fieldsets` entry with `fields: ()`, `classes` containing `"placeholder"` and inline wrapper id (`<formset.prefix>-group`, e.g. `items_set-group`).

## Third-party CSS (`lucus/static/lucus/css/third_party/`)

No extra Python deps. Non-`admin/base.html` staff views: `LUCUS_STAFF_THEME_PATH_PREFIXES` + `lucus.context_processors.staff_integrations_theme`.

| Package | File | Included from |
|---------|------|---------------|
| django-constance | `lucus/css/third_party/constance.css` | `admin/base.html` |
| django-filer | `lucus/css/third_party/filer.css` | `admin/base.html` |
| django-parler | `lucus/css/third_party/parler.css` | `admin/base.html` |
| django-rosetta | `lucus/css/third_party/rosetta.css` | `rosetta/base.html` |
| django-log-viewer (compatible) | `lucus/css/third_party/log_viewer.css` | `log_viewer/logfile_viewer.html` |

## `LUCUS_DASHBOARD`

Context: `lucus_dashboard_columns` from `get_dashboard_for_request`. Section link: `{"label", "url"}` or `{"label", "admin_urlname"}`. Section omitted if no link resolves.

**Layout:** `[{ "column"?: 1–4, "classes"?: str, "sections": [{ "title", "links": [...] }] }, …]`. Same `column` merges sections; `classes` from first dict.

**Groups:** `[{ "column", "title", "links"?: [...], "app_labels"?: set|list|tuple|frozenset }, …]`. `links` then models from `app_labels`; duplicate URLs dropped. `list`/`tuple` `app_labels` preserves order; `set` uses `get_app_list` order.

`LUCUS_DASHBOARD_APPEND_UNCOVERED`: `True` → unreferenced apps to last column; `False` → configured only.

```python
LUCUS_DASHBOARD = [
    {
        "column": 1,
        "classes": "lucus-dashboard__col lucus-grid__col lucus-grid__col--3 lucus-grid__col--md-6 lucus-grid__col--sm-12 lucus-grid__col--xs-12",
        "sections": [
            {
                "title": "Education",
                "links": [
                    {"label": "Instructors", "admin_urlname": "admin:academy_instructor_changelist"},
                    {"label": "Courses", "url": "/admin/academy/course/"},
                ],
            },
        ],
    },
]
```

```python
LUCUS_DASHBOARD = [
    {"column": 1, "title": "Authorization", "app_labels": {"auth"}},
]
```

```python
LUCUS_DASHBOARD = [
    {
        "column": 2,
        "title": "Auth",
        "links": [{"label": "Users", "admin_urlname": "admin:auth_user_changelist"}],
        "app_labels": ("auth",),
    },
]
```

## Stylesheet order

`lucus/css/style.css` → `lucus/css/lucus-admin.css` → `lucus/css/schemes/<slug>.css` → `LUCUS_EXTRA_STATIC_CSS`. Admin widget/inline/action JS: `django.contrib.admin`.

Custom palette: static `lucus/css/<slug>.css` + extend `lucus.theme.BUNDLED_COLOR_SCHEMES`.

`admin/change_list_results.html` overridden: `.text` before `.sortoptions` inside `.lucus-th-heading-inner` (replaces stock float sort icon layout).

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Python modules

| Module | Role |
|--------|------|
| `lucus.apps.LucusConfig` | `ready()`: headers, `each_context`, dashboard context, `lucus_save_ui` / `lucus_save_site`, `enable_nav_sidebar`, `empty_value_display`, `ModelAdmin` action defaults |
| `lucus.dashboard` | Normalize `LUCUS_DASHBOARD` |
| `lucus.models` | `LucusAdminUiPreference` |
| `lucus.theme` | Bundled schemes, `lucus_admin_extra_context` |
| `lucus.views` | POST handlers UI / site |

If you use the header site switcher and want **`request.site`** on each request to match that choice, register **`lucus.sites_panel.LucusAdminSiteMiddleware`** immediately after **`SessionMiddleware`**. Setup details are in the **`lucus.sites_panel`** module.

This repo includes an **`integration/`** demo app and **`requirements-integration.txt`**; optional **`pip install -e ".[integration]"`**. Use the root **`manage.py`** with **`core.settings`**; some demos expect **`sorl.thumbnail`** to be installed.
