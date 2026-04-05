from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LucusAdminUiPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("color_scheme", models.CharField(default="olivia", max_length=64)),
                (
                    "appearance",
                    models.CharField(
                        choices=[("light", "Light"), ("dark", "Dark"), ("auto", "Auto")],
                        default="auto",
                        max_length=10,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lucus_admin_ui_pref",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Lucus admin UI preference",
                "verbose_name_plural": "Lucus admin UI preferences",
            },
        ),
    ]
