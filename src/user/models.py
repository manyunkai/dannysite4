# -*-coding:utf-8 -*-
"""
Created on 2013-10-15

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

import random
import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.http import urlquote
from django.core.mail import send_mail
from django.utils.timezone import utc
from django.conf import settings


class UserManager(BaseUserManager):

    def _create_user(self, username, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password, True, True,
                                 **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    用户 Model
    """

    username = models.CharField('用户名', max_length=75, unique=True, db_index=True)
    email = models.EmailField('邮箱')
    is_staff = models.BooleanField('职员身份', default=False)
    is_active = models.BooleanField('激活状态', default=False)
    date_joined = models.DateTimeField('注册时间', default=timezone.now)

    login_attempted = models.IntegerField('登录失败计次', default=0)
    updated = models.DateTimeField('上次登录尝试', auto_now=True)

    # 2-step verification
    secret = models.CharField(u'密钥', max_length=16, blank=True)
    verification_needed = models.BooleanField(u'启用登录验证', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    backend = 'user.backends.AuthenticationBackend'

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        swappable = 'AUTH_USER_MODEL'

    def is_locked(self):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        if self.login_attempted >= settings.ACCOUNT_LOCK_BY_ATTEMPTED_COUNT:
            if (now - self.updated).seconds < settings.ACCOUNT_LOCK_TIME:
                return True
            else:
                self.login_attempted = 0
                self.save()
        return False

    def incr_login_attempted_count(self):
        self.login_attempted += 1
        self.save()

    def reset_login_attempted_count(self):
        self.login_attempted = 0
        self.save()

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def activate(self):
        self.is_active = True
        self.save()

    def change_secret(self):
        letters = 'abcdefghijklmnopqrstuvwxyz234567'
        self.secret = ''.join(random.sample(letters, 16))


class UserLoginTrack(models.Model):
    """
    用户登录记录 Model
    """

    user = models.ForeignKey(User, verbose_name='用户')

    is_succeed = models.BooleanField('是否成功', default=False)

    created = models.DateTimeField(u'登录时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户登录记录'
        verbose_name_plural = '用户登录记录'
