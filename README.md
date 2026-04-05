# Lucus (Django Admin)

**Read this in another language:** [Русский](README.ru.md)

**Lucus** restyles **django.contrib.admin**: a standalone admin base template, Lucus-owned static (including vendored admin structural CSS under `lucus/static/`), per-user color scheme + appearance, and a configurable multi-column dashboard on `/admin/`. The Django nav sidebar is disabled; change-form actions use a fixed bottom bar.

![Lucus dashboard](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_1.jpg)
![Lucus dashboard](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_2.jpg)
![Lucus dashboard](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_3.jpg)

## Requirements

- Python 3.10+
- Django 5.2+ (see package metadata: `django>=5.2,<7`)

## Installation

```bash
pip install django-lucus
```

Package import name: `lucus`. PyPI project name: **django-lucus**.

## Quick start

Add **Lucus before** `django.contrib.admin` so its templates win:

```python
INSTALLED_APPS = [
    # ...
    "lucus",
    "django.contrib.admin",
    # ...
]
```

Templates and static files ship with the package; run `collectstatic` in production as usual.

After upgrading, run migrations so `LucusAdminUiPreference` exists:

```bash
python manage.py migrate lucus_admin
```

## Settings reference

| Setting | Type | Default | Description |
|--------|------|---------|-------------|
| `SITE_NAME` | `str` | `"Site"` | Used in `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` and optionally as `site_title` |
| `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` | `str` | `"Administration — {site}"` | Passed to `str.format(site=SITE_NAME)` for `admin.site.site_header`. Use only `{site}` unless you escape other braces. |
| `LUCUS_ADMIN_SITE_TITLE_USE_SITE_NAME` | `bool` | `True` | If `True`, `admin.site.site_title` = `SITE_NAME` |
| *(none)* | — | — | **Color scheme** is not a project setting: staff choose **palette + appearance** (light / dark / auto) from header dropdowns; choices are stored in **`LucusAdminUiPreference`** per user. Bundled palettes: `olivia`, `grey`, `slate`, `dune`, `midnight` (`lucus/static/lucus/css/<slug>.css`). |
| `LUCUS_UI` | `dict` | see below | Flags: `help_as_icon`, `high_contrast_toggle` (default `True`). Change-form save bar and changelist actions bar are fixed to the **viewport** bottom. |
| `LUCUS_EXTRA_STATIC_CSS` | `str` \| `list` \| `tuple` | `()` | Extra stylesheet paths (relative to static roots), loaded after the scheme. No `..` or leading `/`. |
| `LUCUS_EMPTY_VALUE_DISPLAY_WRAP` | `bool` | `True` | Wrap empty changelist cells in `<span class="lucus-admin-empty">` |
| `LUCUS_EMPTY_VALUE_PLACEHOLDER` | `str` | `"—"` | Text for `empty_value_display` |
| `LUCUS_ACTIONS_ON_BOTTOM` | `bool` | `True` | Sets **`ModelAdmin.actions_on_bottom = True` on the class** (global for the process) |
| `LUCUS_DASHBOARD` | `list` \| `None` | `None` | Dashboard config (see [Dashboard](#dashboard-lucus_dashboard)); if unset, grouped defaults apply |
| `LUCUS_DASHBOARD_APPEND_UNCOVERED` | `bool` | `True` | In **grouped** mode: append apps not “covered” by groups into the **last** column |

Theme context is built by `lucus.theme.lucus_admin_extra_context(request)` and merged in `admin.site.each_context`.

## Dashboard: `LUCUS_DASHBOARD`

Lucus detects one of two shapes (`lucus.dashboard`: `looks_like_dashboard_layout`, `looks_like_groups_config`).

Template context: **`lucus_dashboard_columns`** — `tuple[DashboardColumn, ...]` from `get_dashboard_for_request(request)`.

Links in a section can use:

- `url` — explicit URL  
- `admin_urlname` — e.g. `admin:app_model_changelist` (resolved with `reverse()`)

A section is shown only if at least one link resolves.

### Mode 1: layout columns

List of dicts with `classes` and/or `sections`. Optional **`column`** in `1..4`: multiple dicts with the same `column` are **merged** (sections concatenated; `classes` from the first dict for that column wins). Column index is clamped to **1–4**.

### Mode 2: column groups

List of dicts with:

- **`column`** (1-based, clamped to ≥ 1; practical grid **1–4**)
- **`title`** — card heading
- **`links`** — optional list of `{"label", "admin_urlname"|"url"}`
- **`app_labels`** — optional `set`, `frozenset`, `list`, or `tuple` of `app_label` strings

Rules:

- Within a group, explicit `links` are listed first (in order), then models from `app_labels`. **URLs are deduplicated.**
- For **`list` / `tuple`** `app_labels`, app order follows that sequence; model order matches the admin.
- For **`set` / `frozenset`**, app order follows `get_app_list`.

**Uncovered apps:** if `LUCUS_DASHBOARD_APPEND_UNCOVERED` is `True`, apps not in the “covered” set are appended to the last column. Covered includes every `app_label` mentioned in groups and apps inferred from successful `admin_urlname` values in `links` (pattern `admin:<app>_<model>_changelist`, longest `app_label` match wins). Set to **`False`** if you want only the groups you defined, with no extra column of leftovers.

### Examples

**Layout with explicit columns:**

```python
LUCUS_DASHBOARD = [
    {
        "column": 1,
        "classes": "lucus-dashboard__col lucus-col lucus-col-3 lucus-col-md-6 lucus-col-sm-12",
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

**Groups with `app_labels`:**

```python
LUCUS_DASHBOARD = [
    {"column": 1, "title": "Authorization", "app_labels": {"auth"}},
]
```

**Mixed `links` + `app_labels`:**

```python
LUCUS_DASHBOARD = [
    {
        "column": 2,
        "title": "Auth",
        "links": [
            {"label": "Users", "admin_urlname": "admin:auth_user_changelist"},
        ],
        "app_labels": ("auth",),
    },
]
```

## Templates and static files

`templates/admin/base.html` is Lucus-owned. CSS load order: `lucus/css/style.css` (layout/tokens), **`lucus/css/lucus-admin.css`** (single admin UI sheet shipped with the package — no `django.contrib.admin` `<link>`), then the palette (`lucus/css/<slug>.css`, overrides tokens), then optional `LUCUS_EXTRA_STATIC_CSS`.

Admin **JavaScript** still comes from `django.contrib.admin` (`admin/js/…`) for widgets, inlines, and actions.

**Bundled palettes** (extend by shipping `static/lucus/css/<slug>.css` and forking `lucus.theme.BUNDLED_COLOR_SCHEMES` in your project if needed):

| File | Role |
|------|------|
| `style.css` | Spacing scale, grid, UI; accents via `var(--lucus-accent)` etc. |
| `olivia.css` | Default green-gray palette |
| `grey.css` | Blue-gray palette |
| `slate.css` | Neutral slate |
| `dune.css` | Warm sand |
| `midnight.css` | Dark / light pairing |

## Package layout

| Module | Role |
|--------|------|
| `lucus.apps.LucusConfig` | `ready()`: site headers, `each_context`, dashboard, theme prefs URL, `enable_nav_sidebar = False`, `empty_value_display`, `actions_on_bottom` |
| `lucus.dashboard` | Config normalization, columns, links |
| `lucus.models` | `LucusAdminUiPreference` (per-user scheme + appearance) |
| `lucus.theme` | Bundled schemes, `lucus_admin_extra_context(request)` |
| `lucus.views` | POST handler for saving UI preferences |

Version: `lucus.__version__` (kept in sync with package metadata on release).

## Compatibility

Lucus targets **Django 5.2+** and is tested against the supported 5.x / 6.x line per `pyproject.toml`.
