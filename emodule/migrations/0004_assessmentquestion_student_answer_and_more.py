# Generated by Django 4.0.2 on 2023-03-11 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emodule', '0003_videolesson_performancetask'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessmentquestion',
            name='student_answer',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='assessmentquestion',
            name='student_correct',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='quizquestion',
            name='student_answer',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='quizquestion',
            name='student_correct',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
