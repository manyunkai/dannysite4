# -*-coding:utf-8 -*-
"""
Created on 2015-05-21

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from .models import Blog


class BlogSitemap(Sitemap):
    """
    博客 Sitemap
    """

    changefreq = 'never'
    priority = 0.8

    def items(self):
        return Blog.objects.filter(is_deleted=False, is_active=True).order_by('-created')

    def lastmod(self, obj):
        return obj.created

    def location(self, obj):
        return reverse('blog_detail', args=[obj.id])
