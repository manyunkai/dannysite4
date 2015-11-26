# -*-coding:utf-8 -*-
"""
Created on 2014-4-4

@author: Danny<manyunkai@hotmail.com>
DannyWork Project.
"""

from __future__ import unicode_literals

import os

from django.db.models.fields.files import ImageField, ImageFieldFile
from django.core.exceptions import ImproperlyConfigured

from tools.imageutils import ImageTrimTools, ImageIOTools


class MultiSizeImageFieldFile(ImageFieldFile):
    """
    对 ImageFieldFile 的拓展，支持获取不同尺寸的图片路径和链接
    """

    def __init__(self, instance, field, name):
        self.config = field.config or {}
        super(MultiSizeImageFieldFile, self).__init__(instance, field, name)

    def _get_dimensions_path(self):
        if not hasattr(self, '_dimensions_path'):
            self._dimensions_path = {}
            for key, value in self.config.items():
                base_path, filename = os.path.split(self.name)
                self._dimensions_path[key] = self.storage.path(os.path.join(base_path, value['dir'], filename))

        return self._dimensions_path
    dimensions_path = property(_get_dimensions_path)

    def _get_dimensions_url(self):
        if not hasattr(self, '_dimensions_url'):
            self._dimensions_url = {}
            for key, value in self.config.items():
                base_path, filename = os.path.split(self.name)
                self._dimensions_url[key] = self.storage.url(os.path.join(base_path, value['dir'], filename))

        return self._dimensions_url
    dimensions_url = property(_get_dimensions_url)

    def save(self, name, content, save=True):
        # name为原文件名，与upload_to等无关
        super(MultiSizeImageFieldFile, self).save(name, content, save)

        dimensions = self.config or {}
        if not type(dimensions) == dict:
            raise ImproperlyConfigured("The configuration of dimensions for the uploading image must be dict.")

        # 保存各尺寸图片
        status, data = ImageIOTools.parse(self.file)
        image = data if status else None
        if dimensions:
            base_path, filename = os.path.split(self.name)
            for dim in dimensions.values():
                if not type(dim) == dict:
                    continue

                try:
                    width, height = dim['size']
                    action, path = dim['action'], dim['dir']
                    #quality = dim['quality']
                except Exception as e:
                    continue

                if action == 'crop':
                    # 按所需大小剪裁
                    manipulated = ImageTrimTools.auto_crop(image, width, height)
                elif action == 'scale':
                    # 缩放图片并保持原比例
                    manipulated = ImageTrimTools.scale(image, width, height)
                else:
                    continue

                path = os.path.join(self.storage.location, base_path, path)
                ImageIOTools.save(manipulated, path, filename)
    save.alters_data = True

    def delete(self, save=True):
        super(MultiSizeImageFieldFile, self).delete(save)
    delete.alters_data = True


class MultiSizeImageField(ImageField):
    """
    对 ImageField 的拓展，支持对设定的多个尺寸进行自动化处理
    """

    attr_class = MultiSizeImageFieldFile

    def __init__(self, verbose_name=None, name=None, config=None, **kwargs):
        self.config = config
        width_field = height_field = None
        super(MultiSizeImageField, self).__init__(verbose_name, name, width_field,
                                                  height_field, **kwargs)

    def pre_save(self, model_instance, add):
        "Returns field's value just before saving."
        file = getattr(model_instance, self.attname)
        if file and not file._committed:
            # Commit the file to storage prior to saving the model
            file.save(file.name, file, save=False)
        return file
