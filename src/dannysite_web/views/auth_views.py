# -*-coding:utf-8 -*-
"""
Created on 2015-05-20

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

import sys

if sys.version_info[0] == 3:
    from urllib.parse import urlparse, urlunparse
else:
    import urllib2
    urlparse, urlunparse = urllib2.urlparse.urlparse, urllib2.urlparse.urlunparse

from django.contrib import auth
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from core.views import AutoTRouteJsonResFormView, AutoTRouteView
from user.forms import LoginForm
from user.models import UserLoginTrack


class Login(AutoTRouteJsonResFormView):
    """
    Login View.
    """

    template_name = 'login.html'
    template_name_m = 'login.html'

    form_class = LoginForm

    redirect_key = 'next'

    def form_valid(self, form):
        user = form.user

        auth.login(self.request, user)

        UserLoginTrack.objects.create(user=user, is_succeed=True)

        data = {
            'redirect': self.request.session.get('login_redirect', reverse('index'))
        }
        return self.render_json_to_response(status=1, data=data)

    def get(self, request, *args, **kwargs):
        redirect = urlparse(request.GET.get(self.redirect_key, '')).path or reverse('index')
        if request.user.is_authenticated():
            return HttpResponseRedirect(redirect)

        request.session['login_redirect'] = redirect

        return super(Login, self).get(request, *args, **kwargs)


class Logout(AutoTRouteView):
    """
    Logout View.
    """

    redirect_key = 'next'

    def get(self, request):
        if request.user.is_authenticated():
            auth.logout(request)

        redirect = urlparse(request.GET.get(self.redirect_key, '')).path \
                   or request.META.get('HTTP_REFERER') or reverse('index')
        return HttpResponseRedirect(redirect)
