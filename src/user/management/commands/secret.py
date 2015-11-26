# -*-coding:utf-8 -*-
"""
Created on 2013-10-15

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from user.models import User


class Command(BaseCommand):
    """
    两步验证密钥重置命令
    """

    def handle(self, *args, **options):
        email = input('请输入要重置密钥的用户邮箱：')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write('无效的用户')
        else:
            user.change_secret()
            user.save()

            self.stdout.write('已重置为：{0}'.format(user.secret))