from django.apps import AppConfig


class LucusConfig(AppConfig):
    name = "lucus"
    label = "lucus_admin"

    def ready(self):
        from django.contrib import admin
        from lucus.dashboard import get_dashboard_for_request

        admin.site.site_header = ""
        admin.site.site_title = ""
        admin.site.index_title = ""

        if not getattr(admin.site, "_lucus_each_context_patched", False):
            original_each_context = admin.site.each_context

            def each_context_with_dashboard(request):
                ctx = original_each_context(request)
                ctx["lucus_dashboard_columns"] = get_dashboard_for_request(request)
                return ctx

            admin.site.each_context = each_context_with_dashboard
            admin.site._lucus_each_context_patched = True

