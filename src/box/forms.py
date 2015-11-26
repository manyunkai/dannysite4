# -*-coding:utf-8 -*-
"""
Created on 2015-05-19

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django import forms

from .models import ImageItem


class ImageItemForm(forms.ModelForm):
    """
    图片对象 Form
    """

    class Meta:
        model = ImageItem
        fields = ['title', 'author', 'description', 'image']
        widgets = {
            'description': forms.Textarea({'cols': '100', 'rows': '5'})
        }
