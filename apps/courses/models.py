from django.db import models
from datetime import datetime
from organizations.models import CourseOrg


# 课程信息表
class Course(models.Model):
    degree_choices = (
        ('elementary', '初级'),
        ('intermediate', '中级'),
        ('advanced', '高级'),
    )
    # null=True, blank=True 因为已经存在了的数据中，这个字段没有值
    course_org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE,
                                   verbose_name=u'课程机构', null=True, blank=True)
    name = models.CharField(max_length=50, verbose_name=u'课程名')
    desc = models.CharField(max_length=300, verbose_name=u'课程描述')
    detail = models.TextField(verbose_name=u'课程详情')
    degree = models.CharField(choices=degree_choices, max_length=10,
                              verbose_name=u'等级')
    learning_time = models.IntegerField(default=0, verbose_name=u'学习时长（分钟）')
    students = models.IntegerField(default=0, verbose_name=u'学习人数')
    fav_nums = models.IntegerField(default=0, verbose_name=u'收藏人数')
    image = models.ImageField(
        upload_to='course/%Y/%m',
        verbose_name=u'封面图',
        max_length=100
    )
    click_nums = models.IntegerField(default=0, verbose_name=u'点击数')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'课程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 章节
class Lesson(models.Model):
    # 一个课程有多个章节。在这里把课程Course设置为外键
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               verbose_name=u'课程')
    name = models.CharField(max_length=100, verbose_name=u'章节名')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'章节'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0} >> {1}'.format(self.course, self.name)


# 每章视频
class Video(models.Model):
    # 把章节设置为外键
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE,
                               verbose_name=u'章节')
    name = models.CharField(max_length=100, verbose_name=u'视频名')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'视频'
        verbose_name_plural = verbose_name


# 课程资源
class CourseResource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               verbose_name=u'课程')
    name = models.CharField(max_length=100, verbose_name=u'名称')
    download = models.FileField(
        upload_to='course/resource/%Y%m',
        verbose_name=u'资源文件',
        max_length=100)
    add_time = models.DateTimeField(default=datetime.now,
                                    verbose_name=u'添加时间'
                                    )

    class Meta:
        verbose_name = u'课程资源'
        verbose_name_plural = verbose_name
