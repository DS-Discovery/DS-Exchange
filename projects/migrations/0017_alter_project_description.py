# Generated by Django 3.2 on 2021-06-28 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0016_alter_project_project_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True, max_length=5000),
        ),
    ]
