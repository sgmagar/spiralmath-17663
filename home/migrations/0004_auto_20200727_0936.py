# Generated by Django 2.2.12 on 2020-07-27 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='path',
            field=models.CharField(blank=True, max_length=200, unique=True),
        ),
    ]