# -*-coding:utf-8 -*-
"""
Created on 2015-05-19

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

import redis

from django.conf import settings


connection = redis.Redis(host=getattr(settings, 'REDIS_HOST', 'localhost'),
                         port=getattr(settings, 'REDIS_PORT', 6379),
                         db=getattr(settings, 'REDIS_DB', 0),
                         password=getattr(settings, 'REDIS_PASSWORD', None),
                         socket_timeout=getattr(settings, 'REDIS_SOCKET_TIMEOUT', None),
                         connection_pool=getattr(settings, 'REDIS_CONNECTION_POOL', None),
                         charset=getattr(settings, 'REDIS_CHARSET', 'utf-8'))
