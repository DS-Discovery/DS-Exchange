# Generated by Django 3.1.1 on 2020-10-13 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0015_auto_20201007_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='id',
            field=models.CharField(default=1666549224046341521, max_length=200, primary_key=True, serialize=False),
        ),
    ]