# Generated by Django 3.1.1 on 2020-12-31 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_remove_answer_question_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='general_question',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]