# -*-coding:utf-8 -*-
"""
Created on 2015-05-21

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django.db import models

from core.models import BaseModel


class Feedback(BaseModel):
    """
    意见反馈 Model
    """

    username = models.CharField('称呼', max_length=64, blank=True)
    email = models.EmailField('邮箱')

    content = models.CharField('反馈内容', max_length=1000)

    ip_address = models.GenericIPAddressField('发布IP', unpack_ipv4=True, blank=True, null=True)

    is_reply = models.BooleanField('是否回复', default=False)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = '用户反馈'
        verbose_name_plural = '用户反馈'


class AccessLog(BaseModel):
    """
    访问日志 Model
    """

    path = models.CharField(u'访问路径', max_length=512, blank=True)
    referer = models.CharField(u'Referer', max_length=512, blank=True)
    agent = models.CharField('User-Agent', max_length=512, blank=True)
    ip_address = models.GenericIPAddressField('IP', unpack_ipv4=True, blank=True, null=True)

    class Meta:
        verbose_name = '访问记录'
        verbose_name_plural = '访问记录'


class ContactConfig(BaseModel):
    """
    站点联系方式配置 Model
    """

    qq = models.CharField('QQ', max_length=16, blank=True)
    weibo = models.URLField('微博链接', blank=True)
    email = models.EmailField('电子邮箱', blank=True)
    github = models.URLField('Github', blank=True)

    def __str__(self):
        return '站点联系方式配置'

    class Meta:
        verbose_name = '站点联系方式配置'
        verbose_name_plural = '站点联系方式配置'


class Link(BaseModel):
    """
    友情链接 Model
    """

    name = models.CharField('显示名称', max_length=50)

    url = models.URLField('链接')
    desc = models.CharField('描述', max_length=500, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '友情链接'
        verbose_name_plural = '友情链接'
