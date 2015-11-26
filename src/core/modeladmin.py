# -*-coding:utf-8 -*-
"""
Created on 2015-05-19

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):
    """
    ModelAdmin 基础类
    """

    def get_queryset(self, request):
        qs = super(BaseModelAdmin, self).get_queryset(request)
        return qs.filter(is_deleted=False)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()