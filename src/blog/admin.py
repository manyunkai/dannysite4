# -*-coding:utf-8 -*-
"""
Created on 2015-05-19

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django.contrib import admin
from django.core.urlresolvers import reverse

from core.modeladmin import BaseModelAdmin
from .forms import BlogForm
from .models import Blog, Theme, Category, Tag, Topic, BlogComment


class BlogAdmin(BaseModelAdmin):
    """
    博客 Admin
    """

    form = BlogForm
    fields = ['title', 'theme', 'cate', 'topic', 'summary', 'content', 'tags', 'is_active']
    list_display = ['title', 'theme', 'cate', 'tag_display', 'created',
                    'click_count', 'comment_list_link', 'is_recommended', 'is_active']
    list_filter = ['theme__name', 'cate__name', 'is_active', 'created']
    list_editable = ['is_recommended', 'is_active']
    search_fields = ['title']

    filter_horizontal = ['tags']

    def tag_display(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])
    tag_display.short_description = '标签'

    def comment_list_link(self, obj):
        url = reverse('admin:blog_blogcomment_changelist') + '?blog__id={0}'.format(obj.id)
        return '<a href="{0}">{1}条评论，点击查看</a>'.format(url, obj.comment_count)
    comment_list_link.short_description = '评论'
    comment_list_link.allow_tags = True


class CAdmin(BaseModelAdmin):
    """
    主题、分类、标签、专题 通用 Admin
    """

    fields = ['name', 'is_active']
    list_display = ['name', 'count', 'created', 'is_active']


class BlogCommentAdmin(BaseModelAdmin):
    """
    博客评论 Admin
    """

    list_display = ['username_display', 'email', 'comment', 'blog_display', 'is_public', 'is_active', 'ip_address', 'created']
    fields = ['user', 'username', 'email', 'comment', 'ip_address', 'is_public', 'is_active']
    list_display_links = None
    list_editable = ['is_public', 'is_active']

    def save_model(self, request, obj, form, change):
        obj.save()

    def username_display(self, obj):
        return '站点用户 {0}'.format(obj.user.username) if obj.user \
            else '访客 {0}'.format(obj.username or obj.ip_address)
    username_display.short_description = '用户'

    def blog_display(self, obj):
        return '<a href="{0}">{1}</a>'.format(reverse('blog_detail', args=[obj.blog.id]), obj.blog.title)
    blog_display.short_description = '所属博客'
    blog_display.allow_tags = True


admin.site.register(Blog, BlogAdmin)
admin.site.register([Theme, Category, Tag, Topic], CAdmin)
admin.site.register(BlogComment, BlogCommentAdmin)
