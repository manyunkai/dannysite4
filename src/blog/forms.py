# -*-coding:utf-8 -*-
"""
Created on 2015-05-20

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django import forms

from ckeditor.widgets import CKEditorWidget
from .models import BlogComment, Blog


class BlogForm(forms.ModelForm):
    """
    博客 Form
    """

    class Meta:
        model = Blog
        fields = ['title', 'theme', 'cate', 'topic', 'summary', 'content', 'tags', 'is_active']
        widgets = {
            'summary': CKEditorWidget()
        }


class CommentForm(forms.Form):
    """
    博客评论 Form
    """

    content = forms.CharField(max_length=500, error_messages={
        'required': '请输入您的留言',
        'max_length': '请确保您的留言不超过500个字符'
    })

    username = forms.CharField(required=False, max_length=64, error_messages={
        'max_length': '请确保您的称呼不超过64个字符'
    })

    email = forms.EmailField(error_messages={
        'invalid': '请正确输入您的电子邮箱以方便与您取得联系',
        'required': '请输入您的电子邮箱以方便与您取得联系'
    })

    def save(self):
        return BlogComment.objects.create(blog=self.initial.get('blog'),
                                          user=self.initial.get('user'),
                                          ip_address=self.initial.get('ip_address'),
                                          comment=self.cleaned_data.get('content'),
                                          username=self.cleaned_data.get('username'),
                                          email=self.cleaned_data.get('email'))
