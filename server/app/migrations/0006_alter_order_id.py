# Generated by Django 3.2.25 on 2024-08-10 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.CharField(default='jRGx0UCgTvk8mpU', editable=False, max_length=15, primary_key=True, serialize=False, unique=True),
        ),
    ]
