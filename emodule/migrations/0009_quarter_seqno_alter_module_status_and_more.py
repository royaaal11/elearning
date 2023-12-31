# Generated by Django 4.0.2 on 2023-03-12 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emodule', '0008_quarter_date_assessment_taken_quarter_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='quarter',
            name='seqno',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='module',
            name='status',
            field=models.CharField(choices=[('Complete', 'Complete'), ('Not yet started', 'Not yet started'), ('No activity', 'No activity')], default='Not yet started', max_length=200),
        ),
        migrations.AlterField(
            model_name='quarter',
            name='status',
            field=models.CharField(choices=[('Complete', 'Complete'), ('Not yet started', 'Not yet started'), ('No activity', 'No activity')], default='Not yet started', max_length=200),
        ),
    ]
