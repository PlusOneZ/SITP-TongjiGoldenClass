# Generated by Django 3.1.7 on 2021-03-17 16:42

import TaskView.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TaskView', '0003_auto_20210317_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedtaskfile',
            name='file',
            field=TaskView.models.RestrictedFileField(upload_to='task/<django.db.models.query_utils.DeferredAttribute object at 0x1056d5970>'),
        ),
    ]
