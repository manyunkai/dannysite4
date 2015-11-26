# -*-coding:utf-8 -*-
"""
Created on 2013-11-06

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from django import template
from django.utils import timezone

register = template.Library()


@register.tag
def get_month(value):
    """
    获取时间的月份英文缩写
    """

    return timezone.localtime(value).strftime('%b') if value else ''

register.filter('month', get_month)
