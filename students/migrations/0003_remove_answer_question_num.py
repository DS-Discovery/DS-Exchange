# Generated by Django 3.1.1 on 2020-12-31 06:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_answer_question'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='question_num',
        ),
    ]
