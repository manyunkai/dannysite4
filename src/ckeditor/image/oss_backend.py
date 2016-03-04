# -*-coding:utf-8 -*-
"""
Created on 2016-03-03

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

try:
    from PIL import Image, ImageOps
except ImportError:
    import Image
    import ImageOps

from ckeditor import utils


def image_verify(f):
    try:
        Image.open(f).verify()
    except IOError:
        raise utils.NotAnImageException


def should_create_thumbnail(file_path):
    return False
