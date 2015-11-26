# -*-coding:utf-8 -*-
"""
Created on 2014-4-3

@author: Danny<manyunkai@hotmail.com>
DannyWork Project.
"""

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.base import ContextMixin, View
from django.views.generic.edit import BaseFormView, ProcessFormView

from .mixins import JsonResFormMixin, AutoTRouteMixin, PaginationMixin, JsonResponseMixin


class JsonResFormView(JsonResFormMixin, BaseFormView):
    """
    A view for displaying a form, and rendering a json response.
    """

    http_method_names = ['post']


class AutoTRouteView(AutoTRouteMixin, ContextMixin, View):
    """
    A view for detecting client's device to return the proper page automatically.
    """


class AutoTRouteJsonResFormView(JsonResFormMixin, AutoTRouteMixin, ProcessFormView):
    """
    Combined JsonResFormView with AutoTRouteJsonResFormView.
    """

    content_type = 'text/html'


class PageView(PaginationMixin, JsonResponseMixin, AutoTRouteView):
    """
    A view for pagination.
    """

    object_list_template_name = None
    object_list_template_name_m = None

    key_name = 'page'

    page_range_left = 3
    page_range_right = 3

    def get_template_names(self):
        if self.request.is_ajax() and self.object_list_template_name:
            return [self.object_list_template_name_m] if self.request.session.get('VIEW_MODE') == 'mobile' \
                and self.object_list_template_name_m else [self.object_list_template_name]

        return super(PageView, self).get_template_names()

    def get_page_data(self, object_list):
        return object_list

    def get_param_list(self):
        params_list = super(PageView, self).get_param_list()
        params_list.append(self.key_name)
        return params_list

    def get_datalist(self):
        """
        Rewrite this func to satisfy your own query needs.
        """

        return super(PageView, self).get_datalist()

    def get(self, request):
        try:
            page = int(request.GET.get(self.key_name))
        except (ValueError, TypeError):
            page = 1

        paginator = self.get_page_items(page)

        context = {
            'num_pages': paginator.num_pages,
            'num_items': paginator.num_items,
            'page_range': paginator.get_page_range(self.page_range_left, self.page_range_right),
            'current_page': paginator.number,
            'has_next': paginator.has_next(),
            'items': self.get_page_data(paginator.object_list)
        }
        context.update(self.get_context_data())

        res = self.render_to_response(context=context, content_type=None)
        if request.is_ajax():
            data = {
                'html': res.rendered_content,
                'has_next': context['has_next']
            }
            return self.render_json_to_response(status=1, data=data)
        return res


def get_404_page(request, *args, **kwargs):
    """
    404 View.
    """

    response = render_to_response('404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def get_500_page(request, *args, **kwargs):
    """
    500 View.
    """

    response = render_to_response('500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response
