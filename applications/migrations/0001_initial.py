# Generated by Django 3.1.1 on 2020-12-31 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('students', '__first__'),
        ('projects', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('rank', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('SUB', 'Submitted'), ('RNI', 'Rejected without interview'), ('RWI', 'Rejected after interview'), ('OFS', 'Offer sent'), ('OFR', 'Offer rejected'), ('OFA', 'Offer accepted')], default='SUB', max_length=3)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.student')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.CharField(max_length=1000)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applications.application')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.question')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.student')),
            ],
        ),
    ]