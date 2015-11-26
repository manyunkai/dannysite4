# -*-coding:utf-8 -*-
"""
Created on 2015-05-20

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from core.views import PageView
from box.models import Box as BoxModel


class Box(PageView):
    """
    Index page of Box.
    """

    template_name = 'box/box.html'
    template_name_m = None

    object_list_template_name = 'box/includes/box_items.html'
    object_list_template_name_m = None

    model = BoxModel
