# Generated by Django 3.1.1 on 2021-01-06 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20210101_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_category',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
