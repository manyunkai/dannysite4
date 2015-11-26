# -*-coding:utf-8 -*-
"""
Created on 2015-05-20

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""


from django import template

register = template.Library()


@register.tag
def get_ip_display(value):
    """
    Filter，对 IP 中间两位进行隐藏处理
    """

    ip_splited = value.split('.')
    if not len(ip_splited) == 4:
        return '*.*.*.*'
    return '.'.join([ip_splited[0], '*', '*', ip_splited[3]])

register.filter('ip', get_ip_display)
