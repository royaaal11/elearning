# Generated by Django 4.0.2 on 2023-03-11 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emodule', '0004_assessmentquestion_student_answer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='direction',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='quiz',
            name='direction',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='assessment',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
