# -*-coding:utf-8 -*-
"""
Created on 2015-05-19

@author: Danny<manyunkai@hotmail.com>
DannyWork Project
"""

from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models import F
from django.db.models.signals import m2m_changed, pre_delete, pre_save, post_save, post_delete

from ckeditor.fields import RichTextField
from comment.models import Comment
from core.models import BaseModel


class Base(BaseModel):
    """
    标签、分类、主题、专题 基础类
    """

    name = models.CharField('名称', max_length=30)

    # 冗余计数
    count = models.IntegerField('引用', default=0)

    def __str__(self):
        return self.name

    def incr(self, num=1):
        self.count = F('count') + num
        self.save()

    def decr(self, num=1):
        self.count = F('count') - num
        self.save()

    class Meta:
        abstract = True


class Tag(Base):
    """
    标签 Model
    """

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'


class Category(Base):
    """
    分类 Model
    """

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'


class Theme(Base):
    """
    主题 Model
    """

    class Meta:
        verbose_name = '主题'
        verbose_name_plural = '主题'


class Topic(Base):
    """
    专题 Model
    """

    class Meta:
        verbose_name = '专题'
        verbose_name_plural = '专题'


class Blog(BaseModel):
    """
    博客 Model
    """

    title = models.CharField('标题', max_length=100)

    theme = models.ForeignKey(Theme, verbose_name='主题')
    cate = models.ForeignKey(Category, verbose_name='分类')
    topic = models.ForeignKey(Topic, verbose_name='专题', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=u'标签')

    # 用于博客首页置顶展示
    is_recommended = models.BooleanField('是否推荐', default=False)

    # 概要，用于列表页显示
    summary = models.CharField(u'概要', max_length=512, blank=True)
    # 博客主体内容
    content = RichTextField('内容')

    # 冗余计数
    click_count = models.IntegerField(u'点击量', default=0, editable=False)
    comment_count = models.IntegerField(u'评论数', default=0, editable=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = u'博客'
        verbose_name_plural = u'博客'

    def click(self, session_key, ip_addr):
        """
        点击统计，将同一 IP 同一 session 视为相同点击

        :param session_key: 会话ID
        :param ip_addr: IP地址
        :return: 返回始终为 None
        """

        from core.cache import connection

        cache_key = settings.BLOG_VISITORS_CACHE_KEY.format(self.id)
        if int(connection.zincrby(cache_key, '{0}-{1}'.format(ip_addr, session_key))) == 1:
            self.click_count = F('click_count') + 1
            self.save()

        if connection.zcard(cache_key) == 1:
            connection.expire(cache_key, settings.BLOG_VISITORS_CACHE_TIMEOUT)

    @property
    def tag_list(self):
        return self.tags.filter(is_deleted=False, is_active=True)


class BlogComment(Comment):
    """
    博客评论 Model，继承自 通用评论
    """

    blog = models.ForeignKey(Blog, verbose_name='所属博客')

    def __str__(self):
        return '来自用户 {0} 对 {1} 的评论'.format(self.username or self.ip_address, self.blog.title)

    class Meta:
        verbose_name = '博客评论'
        verbose_name_plural = '博客评论'


def handle_in_batches(instances, method):
    for instance in instances:
        getattr(instance, method)()


def tags_changed(sender, **kwargs):
    """
    处理标签关联变化，主要是对冗余计数进行加减操作
    """

    if kwargs.get('action') == 'pre_clear':
        handle_in_batches(kwargs.get('instance').tags.all(), 'decr')
    elif kwargs.get('action') == 'post_remove':
        handle_in_batches(Tag.objects.filter(id__in=kwargs.get('pk_set')), 'decr')
    elif kwargs.get('action') == 'post_add':
        handle_in_batches(Tag.objects.filter(id__in=kwargs.get('pk_set')), 'incr')


def blog_pre_save(sender, **kwargs):
    """
    博客保存前，对关联对象的冗余计数进行处理
    """

    curr = kwargs.get('instance')
    try:
        prev = Blog.objects.get(id=curr.id)
    except Blog.DoesNotExist:
        if not curr.is_deleted and curr.is_active:
            curr.theme.incr()
            curr.cate.incr()
    else:
        prev_ps = prev.is_active and not prev.is_deleted
        curr_ps = curr.is_active and not curr.is_deleted
        for item in ['theme', 'cate', 'topic']:
            prev_obj, curr_obj = getattr(prev, item), getattr(curr, item)

            if prev_obj and prev_ps and not curr_ps or prev_ps and prev_obj and not prev_obj == curr_obj:
                prev_obj.decr()

            if curr_obj and curr_ps and not prev_ps or curr_ps and curr_obj and not prev_obj == curr_obj:
                curr_obj.incr()


def blog_pre_delete(sender, **kwargs):
    """
    博客删除前对冗余计数进行处理
    """

    instance = kwargs.get('instance')
    for item in ['theme', 'cate', 'topic']:
        obj = getattr(instance, item)
        if obj:
            obj.decr()
    handle_in_batches(instance.tags.all(), 'decr')


def blogcomment_pre_save(sender, **kwargs):
    """
    评论保存前对冗余计数进行必要的减处理
    """

    instance = kwargs.get('instance')
    if instance.id:
        try:
            old = BlogComment.objects.get(id=instance.id)
        except BlogComment.DoesNotExist:
            return
        if not old.is_deleted and old.is_active and old.is_public:
            blog = old.blog
            blog.comment_count = F('comment_count') - 1
            blog.save()


def blogcomment_post_save(sender, **kwargs):
    """
    评论保存前对冗余计数进行必要的加处理
    """

    instance = kwargs.get('instance')
    if not instance.is_deleted and instance.is_active and instance.is_public:
        blog = instance.blog
        blog.comment_count = F('comment_count') + 1
        blog.save()


def blogcomment_post_delete(sender, **kwargs):
    """
    评论删除前对冗余计数进行必要的减处理
    """

    instance = kwargs.get('instance')
    if not instance.is_deleted and instance.is_active and instance.is_public:
        blog = instance.blog
        blog.comment_count = F('comment_count') - 1
        blog.save()


m2m_changed.connect(tags_changed, sender=Blog.tags.through)
pre_save.connect(blog_pre_save, sender=Blog)
pre_delete.connect(blog_pre_delete, sender=Blog)
pre_save.connect(blogcomment_pre_save, sender=BlogComment)
post_save.connect(blogcomment_post_save, sender=BlogComment)
post_delete.connect(blogcomment_post_delete, sender=BlogComment)
