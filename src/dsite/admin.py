# -*-coding:utf-8 -*-
"""
Created on 2015-05-21

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect

from core.modeladmin import BaseModelAdmin
from .models import Feedback, ContactConfig, Link, AccessLog


class FeedbackAdmin(BaseModelAdmin):
    """
    意见反馈 Admin
    """

    list_display = ['username_display', 'email', 'ip_address', 'created', 'content', 'is_reply_handler']

    actions = None
    list_display_links = None

    def username_display(self, obj):
        return '站点用户 {0}'.format(obj.user.username) if obj.user \
            else '访客 {0}'.format(obj.username or obj.ip_address)
    username_display.short_description = '用户'

    def is_reply_handler(self, obj):
        if obj.is_reply:
            return '已回复'
        return '<a href="{0}">标记为已回复</a>'.format(reverse('admin:dsite_feedback_set_to_replied', args=[obj.id]))
    is_reply_handler.short_description = '回复状态'
    is_reply_handler.allow_tags = True

    def get_urls(self):
        from django.conf.urls import patterns, url

        patterns = patterns(
            '',
            url(r'^(\d+)/set_to_replied/$', self.admin_site.admin_view(self.set_to_replied), name='dsite_feedback_set_to_replied'),
        ) + super(FeedbackAdmin, self).get_urls()
        return patterns

    def set_to_replied(self, request, f_id):
        try:
            feedback = Feedback.objects.get(id=f_id, is_deleted=False)
        except Feedback.DoesNotExist:
            raise Http404

        feedback.is_reply = True
        feedback.save()

        messages.info(request, '标记成功！')

        return HttpResponseRedirect(reverse('admin:dsite_feedback_changelist'))


class ContactConfigAdmin(BaseModelAdmin):
    """
    联系信息配置 Admin
    """

    list_display = ['qq', 'weibo', 'email', 'github']
    fields = ['qq', 'weibo', 'email', 'github', 'is_active']
    actions = None
    list_display_links = None

    def save_model(self, request, obj, form, change):
        obj.is_deleted = False
        obj.save()

    def add_view(self, request, form_url='', extra_context=None):
        config = ContactConfig.objects.all()
        if config.exists():
            return HttpResponseRedirect(reverse('admin:dsite_contactconfig_change', args=[config[0].id]))
        return super(ContactConfigAdmin, self).add_view(request, form_url, extra_context)

    def delete_view(self, request, object_id, extra_context=None):
        ContactConfig.objects.filter(id=object_id).update(is_active=False)

        return HttpResponseRedirect(reverse('admin:dsite_contactconfig_changelist'))


class LinkAdmin(BaseModelAdmin):
    """
    友情链接 Admin
    """

    list_display = ['name', 'url', 'desc', 'is_active']
    fields = ['name', 'url', 'desc', 'is_active']


class AccessLogAdmin(BaseModelAdmin):
    """
    访问记录 Admin
    """

    list_display = ['username_display', 'path', 'referer', 'agent', 'ip_address', 'created']
    actions = None
    list_display_links = None

    def username_display(self, obj):
        return '站点用户 {0}'.format(obj.user.username) if obj.user \
            else '访客 {0}'.format(obj.ip_address)
    username_display.short_description = '用户'


admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(ContactConfig, ContactConfigAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(AccessLog, AccessLogAdmin)
