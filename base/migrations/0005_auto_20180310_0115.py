# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-10 01:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20180308_0514'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='score',
            unique_together=set([('player', 'game')]),
        ),
    ]