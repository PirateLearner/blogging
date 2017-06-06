# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-31 04:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogging', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='title',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='section',
            unique_together=set([('title', 'parent')]),
        ),
    ]
