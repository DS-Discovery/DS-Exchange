# Generated by Django 3.1.1 on 2020-12-02 19:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('email_address', models.EmailField(max_length=100, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100, null=True)),
                ('student_id', models.CharField(max_length=200)),
                ('college', models.CharField(max_length=200)),
                ('major', models.CharField(max_length=200)),
                ('year', models.CharField(max_length=100)),
                ('first_choice', models.CharField(blank=True, max_length=1000, null=True)),
                ('second_choice', models.CharField(blank=True, max_length=1000, null=True)),
                ('third_choice', models.CharField(blank=True, max_length=1000, null=True)),
                ('resume_link', models.CharField(blank=True, max_length=200, null=True)),
                ('general_question', models.CharField(blank=True, max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='tempApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.student')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_num', models.IntegerField()),
                ('answer_text', models.CharField(max_length=1000)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.tempapplication')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.student')),
            ],
        ),
    ]
