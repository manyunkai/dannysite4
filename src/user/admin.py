# -*-coding:utf-8 -*-
"""
Created on 2013-10-15

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

import qrcode
try:
    from StringIO import StringIO as IOClass
except ImportError:
    from io import BytesIO as IOClass

from django.db import transaction
from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.html import escape
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from user.models import User
from user.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm

csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class UserAdmin(admin.ModelAdmin):
    """
    用户 Admin
    """

    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('username', 'email', 'acct_status', 'acct_identity',
                    'date_joined', 'secret_display', 'qrcode_display', 'change_secret_button')
    filter_horizontal = ['groups', 'user_permissions']
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username',)
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        if 'email' in form.changed_data:
            obj.username = obj.email
        obj.save()

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(id=request.user.id)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super(UserAdmin, self).get_form(request, obj, **defaults)

    def get_urls(self):
        from django.conf.urls import patterns
        return patterns('',
            (r'^(\d+)/password/$',
             self.admin_site.admin_view(self.user_change_password))
        ) + super(UserAdmin, self).get_urls()

    def lookup_allowed(self, lookup, value):
        # See #20078: we don't want to allow any lookups involving passwords.
        if lookup.startswith('password'):
            return False
        return super(UserAdmin, self).lookup_allowed(lookup, value)

    @sensitive_post_parameters_m
    @csrf_protect_m
    @transaction.atomic
    def add_view(self, request, form_url='', extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super(UserAdmin, self).add_view(request, form_url,
                                               extra_context)

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = get_object_or_404(self.get_queryset(request), pk=id)
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, request.user, change_message)
                msg = ugettext('Password changed successfully.')
                messages.success(request, msg)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        context.update(admin.site.each_context())
        return TemplateResponse(request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context, current_app=self.admin_site.name)

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determines the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if '_addanother' not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST['_continue'] = 1
        return super(UserAdmin, self).response_add(request, obj,
                                                   post_url_continue)

    def get_urls(self):
        from django.conf.urls import patterns, url

        name_change_secret = '{0}_{1}_change_secret'.format(self.model._meta.app_label, self.model._meta.model_name)
        name_qrcode_img = '{0}_{1}_get_qrcode_image'.format(self.model._meta.app_label, self.model._meta.model_name)

        patterns = patterns(
            '',
            url(r'^(\d+)/change_secret/$', self.admin_site.admin_view(self.change_secret), name=name_change_secret),
            url(r'^get_qrcode_image/$', self.admin_site.admin_view(self.get_qrcode_image), name=name_qrcode_img),
        ) + super(UserAdmin, self).get_urls()
        return patterns

    def change_secret(self, request, id, form_url=''):
        user = get_object_or_404(User, pk=id)
        user.change_secret()
        user.save()

        messages.warning(request, u'密钥已更新，请立即更新您的验证器。')
        return HttpResponseRedirect(reverse('admin:user_user_changelist'))

    def get_qrcode_image(self, request):
        if not request.user.secret:
            raise Http404

        data = 'otpauth://{0}/{1}?secret={2}'.format('totp', request.user.email, request.user.secret)

        qr = qrcode.QRCode(version=5, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()

        img_buffer = IOClass()
        img.save(img_buffer)
        return HttpResponse(img_buffer.getvalue(), 'image/jpeg')

    def qrcode_display(self, user):
        if user.secret:
            return '<img src="{0}" width=150>'.format(reverse('admin:user_user_get_qrcode_image'))
        return '没有可用的密钥'
    qrcode_display.short_description = '二维码'
    qrcode_display.allow_tags = True

    def secret_display(self, user):
        original = user.secret or ''
        i, secret = 0, ''
        while i < len(original):
            secret += original[i]
            if not (i + 1) % 4:
                secret += ' '
            i += 1
        return secret
    secret_display.short_description = u'密钥'

    def change_secret_button(self, user):
        return '<a href="{0}">更换密钥</a>'.format(reverse('admin:user_user_change_secret', args=[user.id]))
    change_secret_button.short_description = u'管理'
    change_secret_button.allow_tags = True

    def acct_status(self, user):
        if not user.is_active:
            return '尚未激活'
        elif user.is_locked():
            return '临时锁定'
        return '正常'
    acct_status.short_description = '账户状态'

    def acct_identity(self, user):
        if user.is_superuser:
            return '超级管理员'
        elif user.is_staff:
            return '管理员'
        return '普通账户'
    acct_identity.short_description = '账户身份'


admin.site.register(Permission)
admin.site.register(User, UserAdmin)
