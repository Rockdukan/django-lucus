from django.apps import AppConfig


class LucusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lucus"
    label = "lucus_admin"

    def ready(self) -> None:
        from django.conf import settings
        from django.contrib import admin
        from django.contrib.admin.options import ModelAdmin
        from django.utils.html import format_html

        from lucus.dashboard import get_dashboard_for_request
        from lucus.sidebar import patch_admin_get_app_list
        from lucus.theme import lucus_admin_extra_context

        site = getattr(settings, "SITE_NAME", "Site")
        header_tpl = getattr(
            settings,
            "LUCUS_ADMIN_SITE_HEADER_TEMPLATE",
            "Administration — {site}",
        )
        admin.site.site_header = header_tpl.format(site=site)
        admin.site.site_title = (
            site if getattr(settings, "LUCUS_ADMIN_SITE_TITLE_USE_SITE_NAME", True) else ""
        )
        admin.site.index_title = ""

        if getattr(settings, "LUCUS_EMPTY_VALUE_DISPLAY_WRAP", True):
            admin.site.empty_value_display = format_html(
                '<span class="lucus-admin-empty">{}</span>',
                getattr(settings, "LUCUS_EMPTY_VALUE_PLACEHOLDER", "—"),
            )

        if getattr(settings, "LUCUS_ACTIONS_ON_BOTTOM", True):
            ModelAdmin.actions_on_bottom = True

        if not getattr(admin.site, "_lucus_each_context_patched", False):
            original_each_context = admin.site.each_context

            def each_context_with_dashboard(request):
                ctx = original_each_context(request)
                ctx["lucus_dashboard_columns"] = get_dashboard_for_request(request)
                ctx.update(lucus_admin_extra_context())
                return ctx

            admin.site.each_context = each_context_with_dashboard
            admin.site._lucus_each_context_patched = True

        if getattr(settings, "LUCUS_SIDEBAR_REORGANIZE", True):
            patch_admin_get_app_list()
