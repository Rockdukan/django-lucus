# Lucus (Django Admin)

**Lucus** is a customization layer for Django Admin: it overrides admin templates and adds a multi-column dashboard on the admin index page.

![Lucus dashboard](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_1.jpg)
![Lucus dashboard](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_2.jpg)
![Lucus dashboard](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_3.jpg)


## Installation

```bash
pip install django-lucus
```

## Configuration

Add Lucus to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "lucus",
    "django.contrib.admin",
    # ...
]
```

After that, Lucus will automatically load its templates and static assets.

### Template precedence (order matters)

Lucus overrides Django admin templates. To make sure Lucus templates are used, `lucus` must be
placed **before** `django.contrib.admin` in `INSTALLED_APPS`.

## Dashboard: `LUCUS_DASHBOARD`

The dashboard on `/admin/` is configured via `settings.LUCUS_DASHBOARD`.

The configuration supports two modes:

1. Full layout config (columns and sections specified directly).
2. Grouped config (automatic link building from the admin by `app_labels`, or explicit `links`).

In all modes:
- Columns `1..4` are supported (1-based numbering).
- A section is shown only if Lucus could resolve at least one link.

You can provide a link in two ways:
- `url` — an explicit URL;
- `admin_urlname` — an admin URL name, e.g. `admin:app_model_changelist` (Lucus will call `reverse()`).

### Mode 1: full layout config

Provide a list of columns as objects:

```python
LUCUS_DASHBOARD = [
    {
        "column": 1,
        "classes": "lucus-dashboard__col ...",
        "sections": [
            {
                "title": "🎓 Education",
                "links": [
                    {"label": "Instructors", "admin_urlname": "admin:academy_instructor_changelist"},
                    {"label": "Courses", "url": "/admin/academy/course/"},
                ],
            },
        ],
    },
    {
        "column": 3,
        "sections": [
            {
                "title": "🛟 Support",
                "links": [
                    {"label": "Tickets", "admin_urlname": "admin:supportdesk_ticket_changelist"},
                ],
            },
        ],
    },
]
```

`column` inside objects is optional, but if it exists, Lucus will place sections into the 1..4 grid.

### Mode 2: grouped config

Provide a list of groups (card sections) in this format:

```python
LUCUS_DASHBOARD = [
    {
        "column": 1,
        "title": "👤  Authorization",
        "app_labels": {"auth"},
    },
]
```

In this variant, the `app_labels` key determines which admin apps to scan for models and build links automatically.

Important:
- `links` in the group is **not** provided (this is the "no links" mode).
- If the admin has no registered models for the provided `app_labels`, the section may not appear.

#### Grouped config with explicit `links`

If you provide `links` instead of `app_labels`, Lucus will use them directly:

```python
LUCUS_DASHBOARD = [
    {
        "column": 2,
        "title": "👤  Authorization",
        "links": [
            {"label": "Users", "admin_urlname": "admin:auth_user_changelist"},
            {"label": "Groups", "admin_urlname": "admin:auth_group_changelist"},
        ],
    },
    {
        "column": 3,
        "title": "🛟 Support",
        "app_labels": {"supportdesk"},
    },
]
```

Behavior note:
- If at least one group provides `links`, Lucus disables auto-adding "the remaining apps" beyond what is listed in `app_labels`.

## Compatibility

Lucus targets Django 5.2+ and supports Django 6.x.

