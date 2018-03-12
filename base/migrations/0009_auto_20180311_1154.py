# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-11 11:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20180311_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='guest_goals',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='home_goals',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='report_number',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
