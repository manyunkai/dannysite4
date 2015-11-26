# -*-coding:utf-8 -*-
"""
Created on 2015-05-19

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django.db import models

from user.models import User


class BaseModel(models.Model):
    """
    模型基础类
    """

    user = models.ForeignKey(User, verbose_name=u'创建者', null=True, blank=True)

    created = models.DateTimeField(u'创建时间', auto_now_add=True)
    updated = models.DateTimeField(u'更新时间', auto_now=True)

    is_deleted = models.BooleanField(u'是否已删除', default=False)
    is_active = models.BooleanField(u'是否激活', default=True)

    class Meta:
        abstract = True
        ordering = ['-created']
