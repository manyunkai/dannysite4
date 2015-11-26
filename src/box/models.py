# -*-coding:utf-8 -*-
"""
Created on 2015-05-19

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

import os
import uuid

from django.db import models

from ckeditor.fields import RichTextField
from core.models import BaseModel
from core.files import MultiSizeImageField


class Box(BaseModel):
    """
    盒子 基础类
    """

    TYPE_CHOICES = (
        ('I', '图片'),
        ('T', '文本')
    )

    type = models.CharField('类型', max_length=1, choices=TYPE_CHOICES)

    title = models.CharField('标题', max_length=32)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '盒子'
        verbose_name_plural = '盒子'


class ImageBox(Box):
    """
    图片盒子 Model
    """

    class Meta:
        verbose_name = '图片盒子'
        verbose_name_plural = '图片盒子'

    @property
    def image(self):
        """
        获取图片，目前仅为一张
        """

        images = self.imageitem_set.filter(is_deleted=False, is_active=True)
        return images[0] if images else None


def image_item_image_upload_to(instance, filename):
    return 'box/image/' + str(uuid.uuid4()) + os.path.splitext(filename)[1]


class ImageItem(BaseModel):
    """
    图片对象
    """

    IMAGE_CONFIG = {
        'thumbnail': {
            'action': 'crop',
            'size': (200, 200),
            'dir': 't',
            'quality': 100
        },
        'normal': {
            'action': 'crop',
            'size': (1200, 600),
            'dir': 'n',
            'quality': 100
        },
    }

    box = models.ForeignKey(ImageBox, verbose_name='所属图片盒子')

    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    description = models.CharField('描述', max_length=256)

    image = MultiSizeImageField('图片', upload_to=image_item_image_upload_to, config=IMAGE_CONFIG)

    def __str__(self):
        return '{0} - {1}'.format(self.box.title, '图片')

    class Meta:
        verbose_name = '图片盒子'
        verbose_name_plural = '图片盒子'


class TextBox(Box):
    """
    文本盒子 Model
    """

    source = models.CharField('引用来源', max_length=128, blank=True)

    content = RichTextField('内容', config_name='basic')

    class Meta:
        verbose_name = '文本盒子'
        verbose_name_plural = '文本盒子'
