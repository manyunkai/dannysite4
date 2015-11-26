# -*-coding:utf-8 -*-
"""
Created on 2013-12-4

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from core.utils import get_client_ip
from dsite.models import AccessLog


class BrowserCheckingMiddleware(object):
    """
    浏览器检测与浏览模式切换中间件
    """

    def process_request(self, request):
        mode = request.session.get('VIEW_MODE')

        change = request.GET.get('change_view_mode')
        if change and change in ['desktop', 'mobile']:
            mode = change
            request.session['VIEW_MODE'] = mode

        if not mode:
            for key in ['iphone', 'android', 'iemobile']:
                if key in request.META.get('HTTP_USER_AGENT', '').lower():
                    mode = 'mobile'
                    break
            mode = 'desktop' if not mode else mode
            request.session['VIEW_MODE'] = mode


class AccessLoggingMiddleware(object):
    """
    用户浏览记录中间件
    """

    def process_request(self, request):
        try:
            AccessLog.objects.create(user=request.user if request.user.is_authenticated() else None,
                                     referer=request.META.get('HTTP_REFERER', ''),
                                     path=request.get_full_path(),
                                     agent=request.META.get('HTTP_USER_AGENT', ''),
                                     ip_address=get_client_ip(request))
        except:
            pass
