# Generated by Django 2.1.4 on 2019-01-04 03:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='link',
            name='player',
        ),
        migrations.RemoveField(
            model_name='link',
            name='user',
        ),
        migrations.DeleteModel(
            name='Link',
        ),
    ]
