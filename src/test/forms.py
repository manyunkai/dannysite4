# -*-coding:utf-8 -*-
"""
Created on 2014-4-9

@author: Danny<manyunkai@hotmail.com>
DannyWork Project.
"""

from django import forms

from core.fields import CustomValidatesImageField

from test.models import Test


class TestForm(forms.ModelForm):
    image = CustomValidatesImageField(label='图片', formats=['png', 'jpg'], min_imagesize=(950, 950), max_filesize=1)

    class Meta:
        model = Test
        fields = ['image', 'oss_image', 'content']