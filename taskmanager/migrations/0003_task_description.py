# Generated by Django 5.1.4 on 2025-01-01 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanager', '0002_rename_subtask_name_subtask_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='description',
            field=models.TextField(default=None),
        ),
    ]
