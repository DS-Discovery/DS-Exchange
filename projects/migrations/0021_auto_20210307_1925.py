# Generated by Django 3.1.2 on 2021-03-08 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0020_auto_20210307_1905'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='cloud_creds',
            field=models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=True),
        ),
        migrations.AddField(
            model_name='project',
            name='hce_intern',
            field=models.CharField(blank=True, choices=[('a', 'Yes'), ('b', 'No'), ('c', 'Maybe')], max_length=1),
        ),
        migrations.AlterField(
            model_name='project',
            name='additional_skills',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='other_num_students',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='technical_requirements',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
