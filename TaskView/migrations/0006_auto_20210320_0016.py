# Generated by Django 3.1.7 on 2021-03-19 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TaskView', '0005_auto_20210318_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='due_time',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
