# Generated by Django 4.0.2 on 2023-03-13 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('emodule', '0009_quarter_seqno_alter_module_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='direction',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='direction',
            field=models.CharField(max_length=1000),
        ),
        migrations.CreateModel(
            name='StudentQuestionAnswers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_id', models.IntegerField()),
                ('is_correct', models.BooleanField(blank=True, null=True)),
                ('group', models.IntegerField()),
                ('assessment_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.assessmentquestion')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.student')),
            ],
        ),
        migrations.CreateModel(
            name='StudentAssessmentResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('date_taken', models.DateTimeField()),
                ('group', models.IntegerField()),
                ('status', models.CharField(choices=[('Passed', 'Passed'), ('Failed', 'Failed')], max_length=100)),
                ('quarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.quarter')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.student')),
            ],
        ),
    ]
