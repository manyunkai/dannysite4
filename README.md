dannysite4
=========

Visit my website at http://www.dannysite.com/


### 介绍

这是 DannySite V4 的源代码。
DannySite 是一个由个人兴趣与学习实践而生的个人网站，网站采用 Django 框架开发。
网站相对于 V3 版本，简化为 Home、Blog 和 Box。
Home 既是首页，也是关于页，简单明了；
Blog 保留了之前的逻辑，只是简化了评论模块；
Box 则是原来“图片”和“兴趣”板块的融合。
另外还有一个 Discovery 页面，包含了意见反馈、友情链接和网站历史等。

### 源码说明

这里的源码包含所有后端逻辑代码，但去掉了除演示模板外的前端代码，包括模板和对应的样式表。

### 基本环境说明

dannysite4 在 Python3 上开发，并做了对 Python2.7 的支持；
Django 请使用 1.8.x 版本。

### 其它包依赖

pymysql==0.6.6
pillow==2.8.1
six==1.9.0
redis==2.10.3
qrcode==5.1
