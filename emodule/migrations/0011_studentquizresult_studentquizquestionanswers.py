# Generated by Django 4.0.2 on 2023-03-13 17:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('emodule', '0010_alter_assessment_direction_alter_quiz_direction_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentQuizResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('date_taken', models.DateTimeField()),
                ('group', models.IntegerField()),
                ('status', models.CharField(choices=[('Passed', 'Passed'), ('Failed', 'Failed')], max_length=100)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.module')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.student')),
            ],
        ),
        migrations.CreateModel(
            name='StudentQuizQuestionAnswers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_id', models.IntegerField()),
                ('is_correct', models.BooleanField(blank=True, null=True)),
                ('group', models.IntegerField()),
                ('quiz_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.quizquestion')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.student')),
            ],
        ),
    ]
