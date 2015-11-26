# -*-coding:utf-8 -*-
"""
Created on 2015-3-22

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django import forms
from django.contrib.auth import authenticate
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX, identify_hasher

from user.models import User
from core.otpauth import OtpAuth


UNMASKED_DIGITS_TO_SHOW = 6


def mask_password(password):
    shown = password[:UNMASKED_DIGITS_TO_SHOW]
    masked = "*" * max(len(password) - UNMASKED_DIGITS_TO_SHOW, 0)
    return shown + masked


class ReadOnlyPasswordHashWidget(forms.Widget):
    def render(self, name, value, attrs):
        encoded = value
        final_attrs = self.build_attrs(attrs)

        if not encoded or encoded.startswith(UNUSABLE_PASSWORD_PREFIX):
            summary = mark_safe('<strong>%s</strong>' % ugettext('No password set.'))
        else:
            try:
                hasher = identify_hasher(encoded)
            except ValueError:
                summary = mark_safe('<strong>%s</strong>' % ugettext(
                    'Invalid password format or unknown hashing algorithm.'))
            else:
                summary = format_html_join('',
                                           '<strong>{0}</strong>: {1} ',
                                           ((ugettext(key), value)
                                            for key, value in hasher.safe_summary(encoded).items())
                                           )

        return format_html('<div{0}>{1}</div>', flatatt(final_attrs), summary)


class ReadOnlyPasswordHashField(forms.Field):
    widget = ReadOnlyPasswordHashWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        super(ReadOnlyPasswordHashField, self).__init__(*args, **kwargs)

    def bound_data(self, data, initial):
        # Always return initial because the widget doesn't
        # render an input field.
        return initial

    def _has_changed(self, initial, data):
        return False


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'duplicate_username': _('A user with that username already exists.'),
        'password_mismatch': _('The two password fields didn\'t match.'),
    }
    email = forms.EmailField(label=_('Email'))
    password1 = forms.CharField(label=_('Password'),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password confirmation'),
        widget=forms.PasswordInput,
        help_text=_('Enter the same password as above, for verification.'))

    class Meta:
        model = User
        fields = []

    def clean_email(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        email = self.cleaned_data['email']
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    email = forms.EmailField(label=_('Email'))
    password = ReadOnlyPasswordHashField(label=_('Password'),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = User
        fields = ['email', 'password', 'is_superuser', 'is_staff',
                  'is_active', 'groups', 'user_permissions', 'verification_needed']

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial['password']


class AdminPasswordChangeForm(forms.Form):
    """
    A form used to change the password of a user in the admin interface.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_('Password'),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password (again)'),
                                widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AdminPasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        """
        Saves the new password.
        """
        self.user.set_password(self.cleaned_data['password1'])
        if commit:
            self.user.save()
        return self.user

    def _get_changed_data(self):
        data = super(AdminPasswordChangeForm, self).changed_data
        for name in self.fields.keys():
            if name not in data:
                return []
        return ['password']
    changed_data = property(_get_changed_data)


class LoginForm(forms.Form):
    """
    Login Form for The main site.
    """

    email = forms.EmailField(error_messages={
        'required': '请输入注册邮箱',
        'invalid': '请输入正确的邮箱',
        'max_length': '邮箱名超长'
    })

    password = forms.CharField(widget=forms.PasswordInput(render_value=False), min_length=6, error_messages={
        'required': '请输入登录密码',
        'min_length': '密码长度不小于6位'
    })

    code = forms.CharField(required=False, min_length=6, max_length=6, error_messages={
        'min_length': '安全代码为6位',
        'max_length': '安全代码为6位'
    })

    user = None

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()

        self.user = authenticate(email=cleaned_data.get('email'),
                                 password=cleaned_data.get('password'))

        if not self.user:
            raise forms.ValidationError(u'用户名或密码不正确')
        if not self.user.is_active:
            raise forms.ValidationError(u'账号尚未激活或被锁定')
        if self.user.is_locked():
            raise forms.ValidationError(u'您的账户应多次尝试登录失败而被暂时锁定')

        if self.user.verification_needed and self.user.secret:
            auth = OtpAuth(self.user.secret)
            if not auth.valid_totp(self.cleaned_data.get('code', '')):
                raise forms.ValidationError(u'安全代码无效')

        return cleaned_data
