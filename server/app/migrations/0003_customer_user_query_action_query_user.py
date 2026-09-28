# Generated manually for endpoint ownership hardening.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def attach_existing_customers_to_first_user(apps, schema_editor):
    Customer = apps.get_model("app", "Customer")
    User = apps.get_model("app", "User")
    first_user = User.objects.order_by("id").first()
    if first_user:
        Customer.objects.filter(user__isnull=True).update(user=first_user)
    else:
        Customer.objects.filter(user__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0002_alter_order_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(
            attach_existing_customers_to_first_user,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="customer",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="query",
            name="action",
            field=models.CharField(default="UNKNOWN", max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="query",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunSQL(
            sql="DELETE FROM query WHERE user_id IS NULL",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name="query",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
