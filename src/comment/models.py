# -*-coding:utf-8 -*-
"""
Created on 2015-05-19

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django.db import models

from core.models import BaseModel


class Comment(BaseModel):
    """
    通用评论
    """

    comment = models.CharField('评论内容', max_length=100)

    username = models.CharField('用户名', max_length=64, blank=True)
    email = models.EmailField(u'邮箱')

    is_public = models.BooleanField('是否公开', default=True)

    ip_address = models.GenericIPAddressField('发布IP', unpack_ipv4=True, blank=True, null=True)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
