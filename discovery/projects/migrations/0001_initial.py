# Generated by Django 3.1.1 on 2020-09-06 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_address', models.EmailField(max_length=254)),
                ('phone_number', models.IntegerField(default=0)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('preferred_name', models.CharField(max_length=20)),
                ('organization', models.CharField(max_length=20)),
                ('job_title', models.CharField(max_length=50)),
                ('hear_from', models.CharField(max_length=50)),
                ('project_name', models.CharField(max_length=50)),
                ('project_category', models.CharField(max_length=50)),
                ('has_data', models.CharField(max_length=20)),
                ('student_num', models.IntegerField(default=0)),
                ('description', models.CharField(max_length=500)),
            ],
        ),
    ]
