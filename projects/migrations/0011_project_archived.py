# Generated by Django 3.1.5 on 2021-01-31 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0010_auto_20210108_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='archived',
            field=models.CharField(default='No', max_length=5000),
        ),
    ]