# Generated by Django 5.1.1 on 2024-09-10 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.CharField(default='HTft0LvunHXCKHm', max_length=15, primary_key=True, serialize=False, unique=True),
        ),
    ]
