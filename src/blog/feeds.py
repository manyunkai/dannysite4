# -*-coding:utf-8 -*-
"""
Created on 2015-05-21

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags

from .models import Blog


class LatestBlogs(Feed):
    """
    博客 RSS
    """

    title = '博客 - DannySite'
    link = '/blog/rss'
    description = '博客 - DannySite'

    def items(self):
        return Blog.objects.filter(is_deleted=False, is_active=True).order_by('-created')[:10]

    def item_title(self, item):
        return item.title

    def item_pubdate(self, item):
        return item.created

    def item_link(self, item):
        link = reverse('blog_detail', args=[item.id])
        return link

    def item_description(self, item):
        description_formated = strip_tags(item.content)
        return description_formated
