# -*-coding:utf-8 -*-
"""
Created on 2013-6-10
@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

import os
from PIL import Image
from PIL import ImageFile


class ImageIOTools(object):
    """
    该类提供一些常用的图片I/O操作方法，包括解析远程图片，打开或关闭本地图片等.
    """

    @classmethod
    def parse(cls, tfile):
        """
        解析远程图片文件, 生成Image类型对象返回
        params:
            file: 从request.FILES中获取的数据对象

        returns:
            img: PIL Image Object
        """

        parser = ImageFile.Parser()
        try:
            for chunk in tfile.chunks():
                parser.feed(chunk)
        except Exception as e:
            return False, str(e)
        finally:
            image = parser.close()

        return True, image

    @classmethod
    def open(cls, tfile):
        """
        通过指定的路径名和文件名打开文件系统内的图片
        params:
            path: 文件所在的主目录
            filename：文件名

        returns:
            img: PIL Image Object
        """

        try:
            image = Image.open(tfile)
        except Exception as e:
            return False, str(e)

        return True, image

    @classmethod
    def save(cls, image, path, filename, format=None, quality=100):
        """
        保存Image对象到文件系统

        params:
            image：PIL Image Object
            path：存储图片文件的主目录
            filename：文件名
            format：保存的格式
            quality：保持的图片质量

        returns：
            执行成功无返回，否则返回相关错误信息
        """

        path = os.path.normpath(path)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception as e:
                return str(e)

        params = {
            'fp': os.path.join(path, filename),
            'quality': quality
        }
        if format:
            params['format'] = format

        try:
            image.save(**params)
        except Exception as e:
            return str(e)


class ImageTrimTools(object):
    @classmethod
    def _crop_with_the_preference_to_width(cls, img, width):
        x, y = img.size

        x_s = width
        y_s = int(y * x_s / x)

        return x_s, y_s

    @classmethod
    def _crop_with_the_preference_to_height(cls, img, height):
        x, y = img.size

        y_s = height
        x_s = int(x * y_s / y)

        return x_s, y_s

    @classmethod
    def auto_crop(cls, image, width, height):
        """
        按指定的高/宽自动剪裁出所需的图片

        params:
            image：PIL Image Object
            width：剪裁的宽度
            height：剪裁的高度

        returns：
            执行成功返回image对象
        """

        if not width and not height:
            return None

        x, y = image.size
        if x <= y:
            x_s, y_s = cls._crop_with_the_preference_to_width(image, width)
            if y_s < height:
                x_s, y_s = cls._crop_with_the_preference_to_height(image, height)
                half_x = int(width / 2)
                half_x_ori = int(x_s / 2)
                XY = (half_x_ori - half_x, 0, half_x_ori + half_x, y_s)
            else:
                half_y = int(height / 2)
                half_y_ori = int(y_s / 2)
                XY = (0, half_y_ori - half_y, x_s, half_y_ori + half_y)
        else:
            x_s, y_s = cls._crop_with_the_preference_to_height(image, height)
            if x_s < width:
                x_s, y_s = cls._crop_with_the_preference_to_width(image, width)
                half_y = int(height / 2)
                half_y_ori = int(y_s / 2)
                XY = (0, half_y_ori - half_y, x_s, half_y_ori + half_y)
            else:
                half_x = int(width / 2)
                half_x_ori = int(x_s / 2)
                XY = (half_x_ori - half_x, 0, half_x_ori + half_x, y_s)

        resized = image.resize((int(x_s), int(y_s)), Image.ANTIALIAS)
        return resized.crop(XY)

    @classmethod
    def crop(cls, image, xy):
        """
        根据指定坐标剪裁图片

        params:
            img: Image object
            xy:  剪切坐标,tuple类型,各坐标点为整数, 形如 (x1, y1, x2, y2)
        return:
            image: 按坐标剪切后的New Image object.
        """

        _image = image.copy()
        _image = _image.crop(xy)
        return _image

    @classmethod
    def scale(cls, img, width=None, height=None):
        """
        按指定的高/宽实现图片缩放

        params:
            image：PIL Image Object
            width：缩放的宽度
            height：缩放的高度

        returns：
            执行成功返回image对象
        """

        x, y = img.size

        if width:
            x_s = width
            y_s = int(y * x_s / x)
        elif height:
            y_s = height
            x_s = int(x * y_s / y)
        else:
            return None

        return img.resize((x_s, y_s), Image.ANTIALIAS)
