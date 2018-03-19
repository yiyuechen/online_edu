from django.db import models
from datetime import datetime
from organizations.models import CourseOrg, Teacher


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
    degree = models.CharField(choices=degree_choices, max_length=15,
                              verbose_name=u'等级')
    learning_time = models.IntegerField(default=0, verbose_name=u'学习时长（分钟）')
    students = models.IntegerField(default=0, verbose_name=u'学习人数')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE,
                                verbose_name=u'教师', null=True, blank=True)
    fav_nums = models.IntegerField(default=0, verbose_name=u'收藏人数')
    category = models.CharField(default=u"后端开发", max_length=20,
                                verbose_name=u'课程类别')
    # 标签，用于依据共同标签推荐课程
    tag = models.CharField(default="", verbose_name=u"课程标签", max_length=30)
    image = models.ImageField(
        upload_to='course/%Y/%m',
        verbose_name=u'封面图',
        max_length=100,
        null=True,
        blank=True
    )
    click_nums = models.IntegerField(default=0, verbose_name=u'点击数')
    # 课程须知
    before_diving_in = models.CharField(default='', max_length=400, verbose_name=u'课程须知')
    # 老师告诉你
    teacher_advice = models.CharField(default='', max_length=400, verbose_name=u'老师告诉你')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'课程'
        verbose_name_plural = verbose_name

    # 获取本课程的章节总数
    def get_chapter_nums(self):
        return self.lesson_set.all().count()

    def get_learning_users(self):
        return self.usercourse_set.all()[:5]

    def get_course_lessons(self):
        """获取课程的章节数目"""
        return self.lesson_set.all().order_by("name")

    def __str__(self):
        return self.name


# 章节 Lesson表示一个课(或章节)，每一课里面有多个视频Video
class Lesson(models.Model):
    # 一个课程有多个章节。在这里把课程Course设置为外键
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               verbose_name=u'课程')
    name = models.CharField(max_length=100, verbose_name=u'章节名')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'章节'
        verbose_name_plural = verbose_name

    def get_lesson_videos(self):
        return self.video_set.all().order_by("name")

    def __str__(self):
        return '{0} >> {1}'.format(self.course, self.name)


# 每章视频
class Video(models.Model):
    # 把章节设置为外键
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE,
                               verbose_name=u'章节')
    name = models.CharField(max_length=100, verbose_name=u'视频名')
    url = models.CharField(max_length=300, default="", verbose_name=u"视频链接")
    learning_time = models.IntegerField(default=0, verbose_name=u'学习时长（分钟）')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'视频'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


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
