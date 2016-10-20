# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-29 19:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alternate',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=64)),
                ('short_name', models.CharField(max_length=64)),
                ('oid', models.CharField(blank=True, max_length=64, null=True)),
                ('logo_data', models.BinaryField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=64)),
                ('short_name', models.CharField(max_length=64)),
                ('oid', models.CharField(blank=True, max_length=64, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(choices=[('rad', 'Radiologo'), ('aut', 'Autenticador'), ('med', 'Medico'), ('hab', 'Habilitador'), ('ree', 'Reemplazador'), ('tec', 'Tecnico'), ('esp', 'Especialista'), ('adm', 'Administrador'), ('cat', 'Catalogador'), ('reg', 'Registrador')], max_length=3)),
                ('institution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='html5dicom.Institution')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=64)),
                ('oid', models.CharField(blank=True, max_length=64, null=True)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='html5dicom.Institution')),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(max_length=20)),
                ('value', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='role',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='html5dicom.Service'),
        ),
        migrations.AddField(
            model_name='role',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='organization',
            unique_together=set([('short_name', 'oid')]),
        ),
        migrations.AddField(
            model_name='institution',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='html5dicom.Organization'),
        ),
        migrations.AddField(
            model_name='alternate',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='html5dicom.Role'),
        ),
        migrations.AddField(
            model_name='alternate',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set([('name', 'oid', 'institution')]),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('name', 'user', 'institution', 'service')]),
        ),
        migrations.AlterUniqueTogether(
            name='institution',
            unique_together=set([('short_name', 'oid', 'organization')]),
        ),
    ]
