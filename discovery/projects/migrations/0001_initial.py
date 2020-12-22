# Generated by Django 3.1.1 on 2020-12-22 04:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('email_address', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=200)),
                ('organization', models.CharField(max_length=100)),
                ('semester', models.CharField(max_length=100)),
                ('year', models.CharField(max_length=100)),
                ('project_category', models.CharField(max_length=100)),
                ('student_num', models.IntegerField(default=0)),
                ('description', models.CharField(max_length=5000)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_num', models.IntegerField(default=0)),
                ('question_text', models.CharField(max_length=200)),
                ('question_type', models.CharField(choices=[('text', 'text'), ('mc', 'multiple choice'), ('dropdown', 'dropdown'), ('checkbox', 'checkbox'), ('multiselect', 'multiselect'), ('range', 'range')], default='text', max_length=50)),
                ('question_data', models.CharField(blank=True, max_length=1000, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
        migrations.CreateModel(
            name='PartnerProjectInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=100)),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.partner')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
        migrations.AddField(
            model_name='partner',
            name='projects',
            field=models.ManyToManyField(to='projects.Project'),
        ),
    ]
