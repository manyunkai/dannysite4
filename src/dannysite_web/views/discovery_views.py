# -*-coding:utf-8 -*-
"""
Created on 2015-05-20

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

import sys
from hashlib import md5

if sys.version_info[0] == 3:
    from urllib.parse import urlparse, urlunparse
else:
    import urllib2
    urlparse, urlunparse = urllib2.urlparse.urlparse, urllib2.urlparse.urlunparse

from django.core.urlresolvers import reverse

from core.utils import get_client_ip
from core.views import AutoTRouteView, JsonResFormView
from dsite.forms import FeedbackForm
from dsite.models import Link


class Discovery(AutoTRouteView):
    """
    View of Discovery Page.
    """

    template_name = 'discovery.html'
    template_name_m = None

    def get(self, request):
        # 为当前用户生成标识符，用于评论表单提交校验
        request.session['discovery-session'] = md5('-'.join(['discovery', 'feedback']).encode()).hexdigest()

        ctx = {
            'links': Link.objects.filter(is_deleted=False, is_active=True)
        }
        return self.render_to_response(context=ctx)


class Feedback(JsonResFormView):
    """
    Feedback Commit View.
    """

    form_class = FeedbackForm

    def get_initial(self):
        initial = super(Feedback, self).get_initial()
        initial.update({
            'user': self.request.user if self.request.user.is_authenticated() else None,
            'ip_address': get_client_ip(self.request)
        })
        return initial

    def post(self, request, *args, **kwargs):
        url = reverse('discovery')
        if not urlparse(self.request.META.get('HTTP_REFERER', '')).path == url:
            return self.render_json_to_response(status=0, msg='验证无效，请尝试刷新后继续提交')

        value = md5('-'.join(['discovery', 'feedback']).encode()).hexdigest()
        if not request.session.get('discovery-session', '') == value:
            return self.render_json_to_response(status=0, msg='验证无效，请尝试刷新后继续提交')

        return super(Feedback, self).post(request, *args, **kwargs)
