# Generated by Django 4.0.2 on 2023-03-10 08:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('date_taken', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Assessment',
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('module_lesson', models.CharField(max_length=200)),
                ('unit_of_competency', models.CharField(max_length=200)),
                ('duration', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('Complete', 'Complete'), ('Not yet started', 'Not yet started')], max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('date_taken', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.module')),
            ],
            options={
                'verbose_name_plural': 'Quizzes',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('full_title', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('profile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='emodule.profile')),
                ('designation', models.CharField(blank=True, max_length=200, null=True)),
            ],
            bases=('emodule.profile',),
        ),
        migrations.CreateModel(
            name='QuizQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.quiz')),
            ],
        ),
        migrations.CreateModel(
            name='QuizChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('is_correct', models.BooleanField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.quizquestion')),
            ],
        ),
        migrations.CreateModel(
            name='Quarter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=200)),
                ('other_title', models.CharField(max_length=200)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.subject')),
            ],
        ),
        migrations.AddField(
            model_name='module',
            name='quarter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.quarter'),
        ),
        migrations.CreateModel(
            name='LearningOutcome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.module')),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.assessment')),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('is_correct', models.BooleanField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.assessmentquestion')),
            ],
        ),
        migrations.AddField(
            model_name='assessment',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.module'),
        ),
        migrations.AddField(
            model_name='subject',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emodule.teacher'),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('profile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='emodule.profile')),
                ('subjects', models.ManyToManyField(to='emodule.Subject')),
            ],
            bases=('emodule.profile',),
        ),
    ]
