# Generated by Django 3.1.7 on 2021-03-24 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TaskView', '0007_auto_20210320_0112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedtaskfile',
            name='index',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
