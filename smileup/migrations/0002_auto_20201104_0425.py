# Generated by Django 2.2.7 on 2020-11-04 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smileup', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='code',
            field=models.CharField(default='__________', max_length=10),
        ),
    ]
