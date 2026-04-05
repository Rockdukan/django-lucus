from django.apps import AppConfig


class LucusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lucus"
    label = "lucus_admin"

    def ready(self) -> None:
        from django.conf import settings
        from django.contrib import admin
        from django.contrib.admin.options import ModelAdmin
        from django.urls import path
        from django.utils.html import format_html

        from lucus import views as lucus_views
        from lucus.admin_list_patch import apply_admin_list_boolean_patch
        from lucus.dashboard import get_dashboard_for_request
        from lucus.theme import lucus_admin_extra_context

        apply_admin_list_boolean_patch()

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

        admin.site.enable_nav_sidebar = False

        if getattr(settings, "LUCUS_EMPTY_VALUE_DISPLAY_WRAP", True):
            admin.site.empty_value_display = format_html(
                '<span class="lucus-admin-empty">{}</span>',
                getattr(settings, "LUCUS_EMPTY_VALUE_PLACEHOLDER", "—"),
            )

        if getattr(settings, "LUCUS_ACTIONS_ON_BOTTOM", True):
            ModelAdmin.actions_on_bottom = True
        if getattr(settings, "LUCUS_ACTIONS_ON_TOP", True):
            ModelAdmin.actions_on_top = True

        if not getattr(admin.site, "_lucus_each_context_patched", False):
            original_each_context = admin.site.each_context

            def each_context_with_dashboard(request):
                ctx = original_each_context(request)
                ctx["lucus_dashboard_columns"] = get_dashboard_for_request(request)
                ctx.update(lucus_admin_extra_context(request))
                return ctx

            admin.site.each_context = each_context_with_dashboard
            admin.site._lucus_each_context_patched = True

        if not getattr(admin.site, "_lucus_get_urls_patched", False):
            original_get_urls = admin.site.get_urls

            def get_urls_with_lucus():
                return [
                    path(
                        "lucus/save-ui/",
                        admin.site.admin_view(lucus_views.save_admin_ui),
                        name="lucus_save_ui",
                    ),
                    path(
                        "lucus/save-site/",
                        admin.site.admin_view(lucus_views.save_admin_site),
                        name="lucus_save_site",
                    ),
                ] + original_get_urls()

            admin.site.get_urls = get_urls_with_lucus
            admin.site._lucus_get_urls_patched = True
