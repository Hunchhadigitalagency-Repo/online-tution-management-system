# Generated by Django 5.0.3 on 2024-03-20 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tution', '0002_alter_classmodel_class_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classmodel',
            name='class_time',
            field=models.CharField(blank=True, default=None, max_length=20),
        ),
    ]
