# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-25 17:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_auto_20170324_2337'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cate',
            options={'verbose_name': '类别', 'verbose_name_plural': '类别管理'},
        ),
        migrations.AlterModelOptions(
            name='news',
            options={'verbose_name': 'SCU动态', 'verbose_name_plural': '动态/创客素材管理'},
        ),
        migrations.AlterModelOptions(
            name='words',
            options={'verbose_name': '创客动态留言', 'verbose_name_plural': '创客动态留言'},
        ),
        migrations.AlterField(
            model_name='news',
            name='new_main',
            field=models.TextField(max_length=100, verbose_name='摘要'),
        ),
    ]
