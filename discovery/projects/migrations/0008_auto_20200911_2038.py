# Generated by Django 3.1.1 on 2020-09-12 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_auto_20200911_2035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='project_name',
            field=models.CharField(max_length=200),
        ),
    ]
