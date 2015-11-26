# -*-coding:utf-8 -*-
"""
Created on 2014-4-5

@author: Danny<manyunkai@hotmail.com>
"""

from django.db import connections

from blog.models import Category, Blog, Theme, Tag, Topic, BlogComment
from user.models import User


def trans_category():

    cursor = connections['old'].cursor()
    cursor.execute("SELECT id, name, count, created FROM `dblog_category`")

    for row in cursor.fetchall():
        Category.objects.create(id=row[0], name=row[1], count=0, created=row[3])


def trans_theme():

    cursor = connections['old'].cursor()
    cursor.execute("SELECT id, name, count, created FROM `dblog_theme`")

    for row in cursor.fetchall():
        Theme.objects.create(id=row[0], name=row[1], count=0, created=row[3])


def trans_topic():

    cursor = connections['old'].cursor()
    cursor.execute("SELECT id, name, count, created FROM `dblog_topic`")

    for row in cursor.fetchall():
        Topic.objects.create(id=row[0], name=row[1], count=0, created=row[3])


def trans_tag():

    cursor = connections['old'].cursor()
    cursor.execute("SELECT id, name, count, created FROM `dblog_tag`")

    for row in cursor.fetchall():
        Tag.objects.create(id=row[0], name=row[1], count=0, created=row[3])


def trans_blog():
    cursor = connections['old'].cursor()
    cursor.execute("SELECT id, title, theme_id, cate_id, topic_id, "
                   "created, updated, content, click_count FROM `dblog_blog`")

    user = User.objects.all()[0]

    for row in cursor.fetchall():
        Blog.objects.create(user=user, id=row[0], title=row[1], theme_id=row[2], cate_id=row[3], topic_id=row[4],
                            created=row[5], updated=row[6], content=row[7], click_count=row[8])


def trans_blog_tags():
    cursor = connections['old'].cursor()
    cursor.execute("SELECT id, blog_id, tag_id FROM `dblog_blog_tags`")

    for row in cursor.fetchall():
        try:
            blog = Blog.objects.get(id=row[1])
        except Blog.DoesNotExist:
            continue
        tag = Tag.objects.get(id=row[2])
        blog.tags.add(tag)


def trans_blog_comments():
    cursor = connections['old'].cursor()
    cursor.execute("select user_name, user_email, comment, submit_date, "
                   "ip_address, content_type_id, object_pk from django_comments")

    for row in cursor.fetchall():
        try:
            blog = Blog.objects.get(id=row[6])
        except Blog.DoesNotExist:
            continue

        BlogComment.objects.create(blog=blog, username=row[0], email=row[1], comment=row[2], created=row[3],
                                   ip_address=row[4])


def trans_all():
    trans_category()
    trans_tag()
    trans_theme()
    trans_topic()
    trans_blog()
    trans_blog_tags()
    trans_blog_comments()
