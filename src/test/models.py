# -*-coding:utf-8 -*-
'''
Created on 2014-4-5

@author: Danny<manyunkai@hotmail.com>
DannyWork Project.
'''

import os
import uuid

from django.db import models

from ckeditor.fields import RichTextField
from core.files import MultiSizeImageField


def upload_to(instance, filename):
    return 'media/test/' + str(uuid.uuid4()) + os.path.splitext(filename)[1]


CONFIG_TEST = {
    'dims': {
        'normal': {
            'action': 'crop',
            'size': (950, 950),
            'dir': '200',
            'quality': 100
        }
    }
}


class Test(models.Model):
    image = MultiSizeImageField(upload_to=upload_to, config=CONFIG_TEST['dims'])
    content = RichTextField(u'内容')

    def __str__(self):
        return self.image.name

    class Meta:
        verbose_name = 'TEST'
        verbose_name_plural = 'TEST'
