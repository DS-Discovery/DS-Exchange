# Generated by Django 3.1.2 on 2021-03-08 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_auto_20210307_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='organization_description',
            field=models.TextField(blank=True, max_length=2000),
        ),
    ]
