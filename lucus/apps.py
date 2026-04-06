from __future__ import annotations

from typing import Any

from django.apps import AppConfig

from lucus.dashboard import get_dashboard_for_request


def _install_staff_integrations_context_processor() -> None:
    """Theme + admin chrome on /logs/, /rosetta/, … (see lucus.context_processors)."""
    from django.conf import settings

    proc = "lucus.context_processors.staff_integrations_theme"
    for tpl in settings.TEMPLATES:
        if tpl.get("BACKEND") != "django.template.backends.django.DjangoTemplates":
            continue
        opts = tpl.setdefault("OPTIONS", {})
        cps = list(opts.get("context_processors") or [])
        if proc not in cps:
            cps.append(proc)
            opts["context_processors"] = cps


def _lucus_admin_site_instances() -> tuple[Any, ...]:
    """AdminSite instances Lucus patches. Default: only ``django.contrib.admin.site``."""
    from django.conf import settings
    from django.contrib import admin
    from django.contrib.admin.sites import AdminSite

    raw = getattr(settings, "LUCUS_ADMIN_SITES", None)
    if raw is None:
        return (admin.site,)
    if isinstance(raw, (list, tuple)):
        sites = tuple(raw)
    else:
        sites = (raw,)
    for s in sites:
        if not isinstance(s, AdminSite):
            raise TypeError(
                "LUCUS_ADMIN_SITES must be an AdminSite or a list/tuple of AdminSite instances, "
                f"got {type(s)!r}"
            )
    return sites


class LucusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lucus"
    label = "lucus_admin"

    def ready(self) -> None:
        from django.conf import settings
        from django.contrib.admin.options import ModelAdmin
        from django.urls import path
        from django.utils.html import format_html

        from lucus import views as lucus_views
        from lucus.admin_list_patch import apply_admin_list_boolean_patch
        from lucus.theme import lucus_admin_extra_context

        apply_admin_list_boolean_patch()

        site_name = getattr(settings, "SITE_NAME", "Site")
        header_tpl = getattr(
            settings,
            "LUCUS_ADMIN_SITE_HEADER_TEMPLATE",
            "Administration — {site}",
        )
        site_title = (
            site_name if getattr(settings, "LUCUS_ADMIN_SITE_TITLE_USE_SITE_NAME", True) else ""
        )

        for admin_site in _lucus_admin_site_instances():
            admin_site.site_header = header_tpl.format(site=site_name)
            admin_site.site_title = site_title
            admin_site.index_title = ""
            admin_site.enable_nav_sidebar = False

            if getattr(settings, "LUCUS_EMPTY_VALUE_DISPLAY_WRAP", True):
                admin_site.empty_value_display = format_html(
                    '<span class="lucus-admin-empty">{}</span>',
                    getattr(settings, "LUCUS_EMPTY_VALUE_PLACEHOLDER", "—"),
                )

            if not getattr(admin_site, "_lucus_each_context_patched", False):
                original_each_context = admin_site.each_context

                def each_context_with_dashboard(
                    request, *, _orig=original_each_context
                ):
                    from django.conf import settings

                    ctx = _orig(request)
                    ctx["lucus_dashboard_columns"] = get_dashboard_for_request(request)
                    ctx.update(lucus_admin_extra_context(request))
                    rm = getattr(request, "resolver_match", None)
                    ctx["lucus_side_dashboard_nav"] = bool(
                        getattr(settings, "LUCUS_SIDE_DASHBOARD_NAV", True)
                        and ctx.get("has_permission")
                        and not ctx.get("is_popup")
                        and rm is not None
                        and rm.url_name != "index"
                    )
                    return ctx

                admin_site.each_context = each_context_with_dashboard
                admin_site._lucus_each_context_patched = True

            if not getattr(admin_site, "_lucus_get_urls_patched", False):
                original_get_urls = admin_site.get_urls

                def get_urls_with_lucus(*, _site=admin_site, _orig=original_get_urls):
                    return [
                        path(
                            "lucus/save-ui/",
                            _site.admin_view(lucus_views.save_admin_ui),
                            name="lucus_save_ui",
                        ),
                        path(
                            "lucus/save-site/",
                            _site.admin_view(lucus_views.save_admin_site),
                            name="lucus_save_site",
                        ),
                    ] + _orig()

                admin_site.get_urls = get_urls_with_lucus
                admin_site._lucus_get_urls_patched = True

        if getattr(settings, "LUCUS_ACTIONS_ON_BOTTOM", True):
            ModelAdmin.actions_on_bottom = True
        if getattr(settings, "LUCUS_ACTIONS_ON_TOP", True):
            ModelAdmin.actions_on_top = True

        _install_staff_integrations_context_processor()
