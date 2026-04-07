from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class LucusAdminUiPreference(models.Model):
    """Per-user admin color scheme and light/dark appearance (Lucus only)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lucus_admin_ui_pref",
    )
    color_scheme = models.CharField(max_length=64, default="olivia")
    appearance = models.CharField(
        max_length=10,
        default="auto",
        choices=(
            ("light", _("Light")),
            ("dark", _("Dark")),
            ("auto", _("Auto")),
        ),
    )

    class Meta:
        db_table = "lucus_admin_lucusadminuipreference"
        verbose_name = _("Lucus admin UI preference")
        verbose_name_plural = _("Lucus admin UI preferences")

    def __str__(self) -> str:
        return f"{self.user_id}: {self.color_scheme} / {self.appearance}"
