# Generated by Django 3.2 on 2021-07-27 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0019_alter_project_skillset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_name',
            field=models.CharField(default='NO NAME', max_length=200),
            preserve_default=False,
        ),
    ]