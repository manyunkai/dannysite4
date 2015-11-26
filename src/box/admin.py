# -*-coding:utf-8 -*-
"""
Created on 2015-05-19

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django.contrib import admin

from core.modeladmin import BaseModelAdmin
from .forms import ImageItemForm
from .models import ImageItem, ImageBox, TextBox


class ImageItemInline(admin.StackedInline):
    """
    图片对象 Inline，用在图片盒子 Admin 中
    """

    model = ImageItem
    max_num = 1
    min_num = 1
    fields = ['title', 'author', 'description', 'image']
    form = ImageItemForm

    def get_queryset(self, request):
        qs = super(ImageItemInline, self).get_queryset(request)
        return qs.filter(is_deleted=False)


class ImageBoxAdmin(BaseModelAdmin):
    """
    图片盒子 Admin
    """

    list_display = ['title', 'created', 'updated', 'is_active']
    fields = ['title', 'is_active']

    inlines = [ImageItemInline]

    def save_model(self, request, obj, form, change):
        obj.type = 'I'
        return super(ImageBoxAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.user = request.user
            instance.save()
        formset.save_m2m()


class TextBoxAdmin(BaseModelAdmin):
    """
    文本盒子 Admin
    """

    list_display = ['title', 'source', 'created', 'updated', 'is_active']
    fields = ['title', 'source', 'content', 'is_active']

    def save_model(self, request, obj, form, change):
        obj.type = 'T'
        return super(TextBoxAdmin, self).save_model(request, obj, form, change)


admin.site.register(ImageBox, ImageBoxAdmin)
admin.site.register(TextBox, TextBoxAdmin)
