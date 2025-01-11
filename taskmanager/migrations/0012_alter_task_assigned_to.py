# Generated by Django 5.1.4 on 2025-01-02 11:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanager', '0011_alter_task_assigned_to'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='assigned_to',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='tasks_assigned', to=settings.AUTH_USER_MODEL),
        ),
    ]
