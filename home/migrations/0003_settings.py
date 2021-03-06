# Generated by Django 2.2.12 on 2020-07-27 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_load_initial_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(blank=True, max_length=200)),
                ('value', models.TextField(blank=True)),
                ('is_deletable', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
