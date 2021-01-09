# Generated by Django 3.1.1 on 2021-01-08 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_project_skillset'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='additional_skills',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='project',
            name='technical_requirements',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='project',
            name='timeline',
            field=models.CharField(blank=True, max_length=1500),
        ),
    ]