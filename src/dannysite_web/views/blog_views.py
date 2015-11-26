# -*-coding:utf-8 -*-
"""
Created on 2015-05-20

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from redis.exceptions import ConnectionError as RedisConnectionError
from hashlib import md5

import sys

if sys.version_info[0] == 3:
    from urllib.parse import urlparse, urlunparse
else:
    import urllib2
    urlparse, urlunparse = urllib2.urlparse.urlparse, urllib2.urlparse.urlunparse

from django.db.models import Q
from django.http import Http404
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateResponseMixin

from core.utils import get_client_ip
from core.views import PageView, AutoTRouteView, JsonResFormView
from blog.models import Blog as BlogModel, Category, Tag
from blog.forms import CommentForm


class Blog(PageView):
    """
    Index page of Box.
    """

    template_name = 'blog/blog.html'
    template_name_m = None

    object_list_template_name = 'blog/includes/blog_items.html'
    object_list_template_name_m = None

    model = BlogModel

    category = None
    tag = None
    q = None
    recommended = None

    def get_url_prefix(self, full_path, cate_id, tag_id, q):
        query = []
        if cate_id:
            query.append('cat={0}'.format(cate_id))
        elif tag_id:
            query.append('tag={0}'.format(tag_id))
        elif q:
            query.append(u'search={0}'.format(q))
        query.append('page=')

        parsed_url = urlparse(full_path)

        return urlunparse((parsed_url.scheme,
                           parsed_url.netloc,
                           parsed_url.path,
                           parsed_url.params,
                           '&'.join(query), ''))

    def get_context_data(self, **kwargs):
        ctx = super(Blog, self).get_context_data(**kwargs)
        ctx['url_prefix'] = self.get_url_prefix(self.request.get_full_path(),
                                                self.category.id if self.category else None,
                                                self.tag.id if self.tag else None,
                                                self.q)

        # 获取分类
        cate_left, cate_right = [], []
        for counter, category in enumerate(Category.objects.filter(is_deleted=False, is_active=True)):
            if counter < 2:
                cate_left.append(category)
            elif counter % 2:
                cate_left.append(category)
            else:
                cate_right.append(category)

        ctx.update({
            'cate_left': cate_left,
            'cate_right': cate_right,
            'recommended': self.recommended,
            'q': self.q
        })
        return ctx

    def get_datalist(self):
        qs = self.model.objects.filter(is_recommended=True, is_active=True, is_deleted=False).order_by('?')
        self.recommended = qs[0] if qs else None

        query = {'is_active': True, 'is_deleted': False}
        if self.category:
            query['cate'] = self.category
        if self.tag:
            query['tags'] = self.tag
        qs = self.model.objects.filter(**query)

        # 排除推荐项
        if self.recommended:
            qs = qs.exclude(id=self.recommended.id)

        # 关键字搜索
        if self.q:
            qs = qs.filter(Q(title__icontains=self.q) |
                           Q(tags__name__icontains=self.q) |
                           Q(content__icontains=self.q)).distinct()

        return qs.order_by('-created') if not self.q else qs.order_by('-click_count')

    def get(self, request):
        cate_id = request.GET.get('cat')
        if cate_id:
            try:
                self.category = Category.objects.get(id=int(cate_id), is_deleted=False, is_active=True)
            except (TypeError, ValueError, Category.DoesNotExist):
                raise Http404
        tag_id = request.GET.get('tag')
        if tag_id:
            try:
                self.tag = Tag.objects.get(id=int(tag_id), is_deleted=False, is_active=True)
            except (ValueError, TypeError, Tag.DoesNotExist):
                raise Http404
        self.q = self.request.GET.get('search')

        return super(Blog, self).get(request)


class Detail(AutoTRouteView):
    """
    Detail page of Blog.
    """

    template_name = 'blog/detail.html'
    template_name_m = None

    def get(self, request, blog_id):
        try:
            blog = BlogModel.objects.get(id=blog_id, is_deleted=False, is_active=True)
        except BlogModel.DoesNotExist:
            raise Http404

        # 浏览计数
        try:
            blog.click(request.session.session_key, get_client_ip(request))
        except RedisConnectionError:
            pass

        # 为当前用户生成标识符，用于评论表单提交校验
        key_name = 'blog-session-{0}'.format(blog.id)
        request.session[key_name] = md5('-'.join(['blog', str(blog.id)]).encode()).hexdigest()

        ctx = {
            'blog': blog,
            'relates': blog.topic.blog_set.filter(is_deleted=False,
                                                  is_active=True).exclude(id=blog.id) if blog.topic else [],
            'comments': blog.blogcomment_set.filter(is_deleted=False, is_active=True).order_by('-created')
        }
        return self.render_to_response(context=ctx)


class Comment(TemplateResponseMixin, JsonResFormView):
    """
    Blog Comment.
    """

    content_type = 'application/json'
    form_class = CommentForm
    template_name = 'blog/includes/comment_item.html'

    blog = None

    def get_initial(self):
        initial = super(Comment, self).get_initial()
        initial.update({
            'ip_address': get_client_ip(self.request),
            'user': self.request.user if self.request.user.is_authenticated() else None,
            'blog': self.blog
        })
        return initial

    def form_valid(self, form):
        comment = form.save()
        res = self.render_to_response({'comment': comment})
        return self.render_json_to_response(status=1, data={'html': res.rendered_content})

    def post(self, request, blog_id, *args, **kwargs):
        try:
            self.blog = BlogModel.objects.get(id=blog_id, is_deleted=False, is_active=True)
        except BlogModel.DoesNotExist:
            return self.render_json_to_response(status=0, msg='无效的博客')

        url = reverse('blog_detail', args=[self.blog.id])
        if not urlparse(self.request.META.get('HTTP_REFERER', '')).path == url:
            return self.render_json_to_response(status=0, msg='验证无效，请尝试刷新后继续提交')

        key_name = 'blog-session-{0}'.format(self.blog.id)
        value = md5('-'.join(['blog', str(self.blog.id)]).encode()).hexdigest()
        if not request.session.get(key_name, '') == value:
            return self.render_json_to_response(status=0, msg='验证无效，请尝试刷新后继续提交')

        return super(Comment, self).post(request, *args, **kwargs)
