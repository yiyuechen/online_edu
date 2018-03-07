from django.db import models
from datetime import datetime

from users.models import UserProfile
from courses.models import Course


# 用户我要学习表单
class UserAsk(models.Model):
    name = models.CharField(max_length=20, verbose_name=u'姓名')
    mobile = models.CharField(max_length=11, verbose_name=u'手机')
    course_name = models.CharField(max_length=50, verbose_name=u'课程名')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'用户咨询'
        verbose_name_plural = verbose_name


# 用户课程评价
class CourseComments(models.Model):
    # 两个外键：用户和课程
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               verbose_name=u'课程')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                             verbose_name=u'用户')
    comments = models.CharField(max_length=250, verbose_name=u'评论')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'评论时间')

    class Meta:
        verbose_name = u'课程名称'
        verbose_name_plural = verbose_name


# 用户对于课程，机构，讲师的收藏
class UserFavorite(models.Model):
    # 涉及四个外键
    type_choices = (
        (1, u'课程'),
        (2, u'课程机构'),
        (3, u'讲师')
    )

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                             verbose_name=u'用户')
    # 保存用户id
    fav_id = models.IntegerField(default=0)
    # 收藏的信息种类
    fav_type = models.IntegerField(
        choices=type_choices,
        default=1,
        verbose_name=u'收藏类型'
    )
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'评论时间')

    class Meta:
        verbose_name = u'用户收藏'
        verbose_name_plural = verbose_name


# 用户消息表
class UserMessage(models.Model):
    # 有两种消息，一种发给单个用户，一种发给全体
    # 无法使用外键实现即给单个用户
    # 可以用default值来确定，default为0，则发给所有用户
    user = models.IntegerField(default=0, verbose_name=u'接收用户')
    message = models.CharField(max_length=500, verbose_name=u'消息内容')

    # 是否已读， True表示已读
    has_read = models.BooleanField(default=False, verbose_name=u'是否已读')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'用户消息'
        verbose_name_plural = verbose_name


# 用户课程表
class UserCourse(models.Model):
    # 涉及两个外键：用户和课程
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               verbose_name=u'课程')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                             verbose_name=u'用户')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'用户课程'
        verbose_name_plural = verbose_name
