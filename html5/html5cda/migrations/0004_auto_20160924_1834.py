# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-24 18:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('html5cda', '0003_auto_20160924_1827'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Susbsec',
            new_name='Subsec',
        ),
        migrations.RenameModel(
            old_name='Susbsubsec',
            new_name='Subsubsec',
        ),
        migrations.RenameField(
            model_name='subsec',
            old_name='idsusbsec',
            new_name='idsubsec',
        ),
        migrations.RenameField(
            model_name='subsubsec',
            old_name='idsusbsubsec',
            new_name='idsubsubsec',
        ),
        migrations.AlterModelTable(
            name='subsec',
            table='subsec',
        ),
        migrations.AlterModelTable(
            name='subsubsec',
            table='subsubsec',
        ),
    ]