# -*-coding:utf-8 -*-
"""
Created on 2014-4-3

@author: Danny<manyunkai@hotmail.com>
DannyWork Project.
"""

from __future__ import unicode_literals

import six
import time
import math
import json
import datetime

from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import RawQuerySet
from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin, ModelFormMixin


class JsonResponseMixin(object):
    """
    提供 render_json_to_response 方法支持以既定格式返回 Json 数据
    """

    content_type = 'application/json'

    def render_json_to_response(self, status, msg='', **kwargs):
        data = kwargs.get('data', {})
        data['status'] = status
        if msg:
            data['message'] = msg

        return HttpResponse(json.dumps(data), content_type=self.content_type)


class JsonResFormMixin(FormMixin, JsonResponseMixin):
    """
    JsonResFormView 使用到的 Mixin，提供 form_valid 和 form_invalid 方法提供 Json 数据类型返回
    """

    def form_valid(self, form):
        if hasattr(form, 'save'):
            form.save()

        return self.render_json_to_response(status=1, msg='success')

    def form_invalid(self, form):
        return self.render_json_to_response(status=0, msg=','.join(form.errors.popitem()[1]))


class JsonResModelFormMixin(ModelFormMixin, JsonResponseMixin):
    """
    与 JsonResFormMixin 不同的是，这里封装的 form_valid 默认会调用 ModelForm 的 save() 方法做数据保存操作
    """

    def form_valid(self, form):
        self.object = form.save()
        return self.render_json_to_response(status=1, msg='success')

    def form_invalid(self, form):
        return self.render_json_to_response(status=0, msg=','.join(form.errors.popitem()[1]))


class AutoTRouteMixin(TemplateResponseMixin):
    """
    自动选择 桌面版 或 手机版 模板，
    需配合 BrowserCheckingMiddleware 使用
    """

    template_name = None
    template_name_m = None

    response_class = TemplateResponse
    content_type = None

    def get_template_names(self):
        """
        Returns a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            return [self.template_name_m] if self.request.session.get('VIEW_MODE') == 'mobile' and self.template_name_m else [self.template_name]


class _Page(object):

    def __init__(self, object_list, number, num_pages, num_items):
        self.object_list = object_list
        self.number = number
        self.num_pages = num_pages
        self.num_items = num_items

    def __repr__(self):
        return '<Page %s of %s>' % (self.number, self.num_pages)

    def __len__(self):
        return len(self.object_list)

    def __getitem__(self, index):
        if not isinstance(index, (slice,) + six.integer_types):
            raise TypeError
        # The object_list is converted to a list so that if it was a QuerySet
        # it won't be a database hit per __getitem__.
        if not isinstance(self.object_list, list):
            self.object_list = list(self.object_list)
        return self.object_list[index]

    def has_next(self):
        return self.number < self.num_pages

    def has_previous(self):
        return self.number > 1

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    def get_page_range(self, left=3, right=3):
        page_range = [self.number]
        # left
        for i in range(1, left):
            page_num = self.number - i
            if page_num <= 0:
                break
            page_range.insert(0, page_num)
        # right
        for i in range(1, right):
            page_num = self.number + i
            if page_num > self.num_pages:
                break
            page_range.append(page_num)
        return page_range

    # def next_page_number(self):
    #
    # def previous_page_number(self):


class PaginationMixin(object):
    """
    A pagination mixin.
    Notice that this mixin relies on HttpRequest for session cache.
    """

    model = None
    items_per_page = 10

    def get_cache_key(self):
        return '{0}_{1}'.format(self.model.__name__, 'fst_req_t')

    def get_timestamp(self, key):
        t = self.request.session.get(key)
        if not t:
            return None
        t = datetime.datetime.fromtimestamp(t)
        t = t.replace(tzinfo=timezone.utc)
        return t

    def set_timestamp(self, key, dt):
        t = time.mktime(dt.timetuple())
        self.request.session[key] = t

    def get_datalist(self):
        """
        按查询条件得到的所有数据，返回queryset

        :return: model's queryset.
        """

        return self.model.objects.filter(is_deleted=False, is_active=True).order_by('-created')

    def queryset(self, t):
        qs = self.get_datalist()
        return qs if isinstance(qs, RawQuerySet) else qs.filter(created__lte=t)

    def get_page_items(self, page):
        if not isinstance(page, int):
            page = 1
        elif page < 1:
            page = 1

        t = self.get_timestamp(self.get_cache_key())
        if not t or page == 1:
            t = timezone.localtime(timezone.now())
            self.set_timestamp(self.get_cache_key(), t)
        qs = self.queryset(t)

        # 获取总数和分页数
        total = qs.count()
        num_pages = math.ceil(total / float(self.items_per_page))

        # 如果超过最后一页，则将 page 置为最后一页
        page = num_pages if num_pages and page > num_pages else page

        # 获取分页数据
        if isinstance(qs, RawQuerySet):
            ctx = {
                'raw_query': qs.query.sql,
                'limit': self.items_per_page,
                'offset': (page - 1) * self.items_per_page
            }
            qs.query.sql = "{raw_query} LIMIT {limit} OFFSET {offset}".format(**ctx)
            object_list = qs
        else:
            object_list = qs[(page - 1) * self.items_per_page:page * self.items_per_page]

        return _Page(object_list=object_list, number=page, num_pages=num_pages, num_items=total)
