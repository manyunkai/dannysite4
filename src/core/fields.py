# -*-coding:utf-8 -*-
"""
Created on 2014-4-9

@author: Danny<manyunkai@hotmail.com>
DannyWork Project.
"""

from __future__ import unicode_literals

import os

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.forms import ImageField


class CustomValidatesImageField(ImageField):
    """
    自定义 ImageField，可对上传文件的大小、格式、尺寸进行校验限制
    """

    default_error_messages = {
        'invalid_image': "您上传的文件无法解析为图片",
        'invalid_format': "您上传的图片格式不被支持",
        'file_too_large': "您上传的文件太大",
        'size_too_small': "您上传的图片尺寸太小以至于无法保证显示质量"
    }

    def __init__(self, *args, **kwargs):
        self.valid_formats = kwargs.pop('formats', None)
        self.max_filesize = kwargs.pop('max_filesize', None)
        self.min_imagesize = kwargs.pop('min_imagesize', None)
        super(CustomValidatesImageField, self).__init__(*args, **kwargs)

    def validate(self, value):
        if not value:
            return

        if self.valid_formats and not os.path.splitext(value.name)[1][1:] in self.valid_formats:
            raise ValidationError(self.error_messages['invalid_format'], code='invalid_format')
        if self.max_filesize and value.size > self.max_filesize * 1024 * 1024:
            raise ValidationError("您上传的图片大小应小于{0}M".format(self.max_filesize), code='file_too_large')
        if self.min_imagesize:
            w, h = get_image_dimensions(value)
            if w < self.min_imagesize[0] or h < self.min_imagesize[1]:
                raise ValidationError("为保证显示质量，您上次的图片尺寸应不小于{0} x {1}".format(*self.min_imagesize),
                                      code='size_too_small')
