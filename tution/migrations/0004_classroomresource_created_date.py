# Generated by Django 5.0.3 on 2024-03-20 10:27

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tution', '0003_alter_classmodel_class_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroomresource',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
