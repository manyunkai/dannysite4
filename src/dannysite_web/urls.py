# -*-coding:utf-8 -*-
"""
Created on 2015-05-20

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from functools import partial

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

admin.autodiscover()

from blog.feeds import LatestBlogs
from blog.sitemap import BlogSitemap
from .views.box_views import Box
from .views.blog_views import Blog, Detail, Comment
from .views.discovery_views import Feedback, Discovery
from .views.auth_views import Login, Logout
from .views.site_views import ContactRedirect

sitemaps = {
    'blog': BlogSitemap
}

handler404 = 'core.views.get_404_page'
handler500 = 'core.views.get_500_page'


urlpatterns = patterns(
    '',
    url(r'^ckeditor/', include('ckeditor.urls')),

    url(r'^$', TemplateView.as_view(template_name='sample.html'), name='index'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^box/$', Box.as_view(), name='box'),

    url(r'^blog/$', Blog.as_view(), name='blog'),
    url(r'^blog/(\d+)/$', Detail.as_view(), name='blog_detail'),
    url(r'^blog/(\d+)/comment/$', Comment.as_view(), name='blog_comment'),
    url(r'^blog/rss/$', LatestBlogs(), name='blog_rss'),

    url(r'^discovery/$', Discovery.as_view(), name='discovery'),
    url(r'^feedback/$', Feedback.as_view(), name='feedback'),

    url(r'^auth/login/$', Login.as_view(), name='login'),
    url(r'^auth/logout/$', Logout.as_view(), name='logout'),

    url(r'^site/contact/$', ContactRedirect.as_view(), name='contact_redirect'),

    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
