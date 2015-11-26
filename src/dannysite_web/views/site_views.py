# -*-coding:utf-8 -*-
"""
Created on 2015-05-20

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirectBase

from core.views import AutoTRouteView
from dsite.models import ContactConfig


class HttpResponseRedirect(HttpResponseRedirectBase):
    allowed_schemes = ['http', 'https', 'mailto']
    status_code = 302


class ContactRedirect(AutoTRouteView):
    """
    Redirect View of Contact icon clicking.
    """

    def get(self, request):
        c_type = request.GET.get('type', '')
        if c_type in ['qq', 'weibo', 'email', 'github']:
            c = ContactConfig.objects.filter(is_deleted=False, is_active=True)
            if c:
                v = getattr(c[0], c_type)
                if c_type == 'qq':
                    href = 'http://wpa.qq.com/msgrd?V=1&amp;Uin={0}&amp;Site=www.dannysite.com&amp;Menu=yes'.format(v)
                elif c_type == 'email':
                    href = 'mailto:{0}'.format(v)
                else:
                    href = v
                return HttpResponseRedirect(href)
        return HttpResponseRedirect(reverse('index'))
