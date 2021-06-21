# Generated by Django 3.1.5 on 2021-05-31 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0016_auto_20210531_0218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_category',
            field=models.CharField(choices=[('a', 'Academia'), ('b', 'Social Sector'), ('c', 'Startup'), ('d', 'Other')], default='a', max_length=100),
        ),
    ]