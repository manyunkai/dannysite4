# -*-coding:utf-8 -*-
"""
Created on 2016-03-03

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

import os

import oss2

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage, urljoin


class AliOSSStorage(Storage):
    """
    阿里云 OSS 存储

    options = {
        'bucket': 'your bucket',
        'location': 'location prefix',
        'base_url': 'url prefix when requesting',
        'image_process_base_url': 'url prefix when requesting processed image',
        'image_process_rule': '',
        'endpoint': 'endpoint',
        'access_key': 'your access key',
        'access_key_secret': 'your access key secret'
    }
    """

    def __init__(self, options=None):
        self.options = settings.OSS_OPTIONS if options is None else options

        auth = oss2.Auth(self.options['access_key'], self.options['access_key_secret'])
        self.bucket = oss2.Bucket(auth, self.options['endpoint'], self.options['bucket'])

    def path(self, name):
        path = os.path.normpath(os.path.join(self.options.get('location', ''), name))
        if not os.path.sep == '/':
            path = '/'.join(path.split(os.path.sep))
        return path

    def _save(self, name, content):
        full_path = self.path(name)

        # put object to oss.
        self.bucket.put_object(full_path, content)

        return name

    def _open(self, name, mode='rb'):
        full_path = self.path(name)

        # get object content.
        stream = self.bucket.get_object(full_path)

        return ContentFile(stream.read())

    def delete(self, name):
        self.bucket.delete_object(name)

    def listdir(self, path):
        full_path = self.path(path)
        if not full_path.endswith('/'):
            full_path += '/'
        directories, files = [], []
        for obj in oss2.ObjectIterator(self.bucket, prefix=full_path, delimiter='/'):
            key = obj.key[len(full_path):].rstrip('/')
            if not key:
                continue
            l = directories if obj.is_prefix() else files
            l.append(key)
        return directories, files

    def url(self, name):
        base_url = self.options.get('base_url')
        if base_url is None:
            raise ValueError('This file is not accessible via a URL.')
        return urljoin(base_url, name)

    def image_processed_url(self, name):
        base_url, rule = self.options.get('image_process_base_url'), self.options.get('image_process_rule')
        if base_url is None or not rule:
            raise ValueError('This file\'s thumb is not valuable.')
        return urljoin(base_url, name + rule)

    def exists(self, name):
        path = self.path(name)
        return self.bucket.object_exists(path)
