# -*-coding:utf-8 -*-
"""
Created on 2015-05-21

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django import forms

from .models import Feedback


class FeedbackForm(forms.Form):
    """
    意见反馈 Form
    """

    content = forms.CharField(max_length=1000, error_messages={
        'required': '请输入您的反馈内容',
        'max_length': '请确保您的反馈内容不超过1000个字符'
    })

    username = forms.CharField(required=False, max_length=64, error_messages={
        'max_length': '请确保您的称呼不超过64个字符'
    })

    email = forms.EmailField(error_messages={
        'invalid': '请正确输入您的电子邮箱以方便与您取得联系',
        'required': '请输入您的电子邮箱以方便与您取得联系'
    })

    def save(self):
        return Feedback.objects.create(user=self.initial.get('user'),
                                       ip_address=self.initial.get('ip_address'),
                                       content=self.cleaned_data.get('content'),
                                       username=self.cleaned_data.get('username'),
                                       email=self.cleaned_data.get('email'))
