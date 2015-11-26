# -*-coding:utf-8 -*-
"""
Created on 2014-4-5

@author: Danny<manyunkai@hotmail.com>
"""

from django.contrib import admin

from test.forms import TestForm
from test.models import Test


class TestAdmin(admin.ModelAdmin):
    form = TestForm


admin.site.register(Test, TestAdmin)
