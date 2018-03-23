from django.shortcuts import render
from django.views.generic import View
from courses.models import Course, CourseResource, Video
from django.db.models import Q

from django.http import HttpResponse

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from operation.models import UserFavorite, CourseComments, UserCourse
from utils.mixin_utils import LoginRequiredMixin


class CourseListView(View):
    def get(self, request):
        courses = Course.objects.all().order_by("-add_time")
        # 右侧栏热门课程
        hot_courses = Course.objects.all().order_by("-click_nums")[:3]

        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            courses = courses.filter(Q(name__icontains=search_keywords) | Q(
                desc__icontains=search_keywords) | Q(
                detail__icontains=search_keywords))

        # 由学习人数和课程数进行排序筛选
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                courses = courses.order_by("-students")
            elif sort == 'hot':
                courses = courses.order_by("-click_nums")

        # 对课程机构进行分页
        # 尝试获取前台get请求传递过来的page参数
        # 如果是不合法的配置参数默认返回第一页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 这里取3个出来，每页显示3个
        p = Paginator(courses, 3, request=request)
        courses = p.page(page)

        return render(request, 'course-list.html', {
            'courses': courses,
            'hot_courses': hot_courses,
            'sort': sort
        })


class CourseDetailView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)
        # 增加点击数
        course.click_nums += 1
        course.save()

        # 判断收藏
        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id,
                                           fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user,
                                           fav_id=course.course_org.id,
                                           fav_type=2):
                has_fav_org = True

        tag = course.tag
        # 如果有tag
        if tag:
            related_courses = Course.objects.filter(tag=tag)[:1]
            # ***以下代码存在问题*** #
            # all_related_courses = Course.objects.filter(tag=tag)
            # related_courses =[]
            # for course in all_related_courses:
            #     if int(course.id) == int(course_id):
            #         related_courses.append(course)
            # ******************* #
        else:
            # 如果是空，传一个空数组，否则是空字符串，在html中遍历会出错
            related_courses = []
        return render(request, 'course-detail.html', {
            'course': course,
            'related_courses': related_courses,
            'has_fav_course': has_fav_course,
            'has_fav_org': has_fav_org,
        })


class CourseInfoView(LoginRequiredMixin, View):
    """课程章节信息"""

    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)
        course_resource = CourseResource.objects.filter(course=course)
        # ?
        # course_resource = CourseResource.objects.get(id=course_id)

        # 先在user_course表中查询这个用户是否已经关联这个课程，如果不是的话，就保存一条关联记录
        user_courses = UserCourse.objects.filter(
            user=request.user,
            course=course
        )

        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 先根据course对应实例化一个user_courses的操作类
        user_courses = UserCourse.objects.filter(course=course)
        # 把这个实例中的所有对应的用户取出来，放入user_ids
        user_ids = [user_course.user.id for user_course in user_courses]
        # 使用了__in规则表示只要user_id等于user_ids数组中的任何一个，都满足
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程ID
        course_ids = [user_course.course.id for user_course in
                      all_user_courses]
        # 获取其他课程
        related_courses = Course.objects.filter(id__in=course_ids).order_by(
            "-click_nums")[:5]
        return render(request, 'course-video.html', {
            'course': course,
            'course_resource': course_resource,
            'user_courses': user_courses,
            'related_courses': related_courses
        })


class CourseCommentsView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)
        course_resource = CourseResource.objects.filter(course=course)
        comments = CourseComments.objects.all()
        return render(request, 'course-comment.html', {
            'course': course,
            'course_resource': course_resource,
            'comments': comments
        })


class AddCommentsView(View):
    """添加课程评论"""

    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}',
                                content_type='application/json')
        course_id = request.POST.get("course_id", 0)
        comments = request.POST.get("comments", "")
        if int(course_id) > 0 and comments:
            course_comment = CourseComments()
            # get只取出一条，如果满足多条或没有，就异常，filter返回数组，不会抛异常
            course = Course.objects.get(id=int(course_id))
            course_comment.course = course
            course_comment.comments = comments
            course_comment.user = request.user
            course_comment.save()
            return HttpResponse('{"status":"success", "msg":"添加成功"}',
                                content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加失败"}',
                                content_type='application/json')


# 播放视频的view
class VideoPlayView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, video_id):
        # id是数据表里面默认为我们添加的值。
        video = Video.objects.get(id=int(video_id))
        # 找到对应的course
        course = video.lesson.course
        # 查询用户是否开始学习了该课
        user_courses = UserCourse.objects.filter(user=request.user,
                                                 course=course)
        # 如果还未学习则加入用户课程表
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()
        # 查询课程资源
        all_resources = CourseResource.objects.filter(course=course)
        # 选出学了这门课的学生关系
        user_courses = UserCourse.objects.filter(course=course)
        # 从关系中取出user_id
        user_ids = [user_course.user_id for user_course in user_courses]
        # 这些用户学了的课程,外键会自动有id，取到字段
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_course.course_id for user_course in
                      all_user_courses]
        # 获取学过该课程用户学过的其他课程
        related_courses = Course.objects.filter(id__in=course_ids).order_by(
            "-click_nums").exclude(id=course.id)[:4]
        # 是否收藏课程
        return render(request, "course-play.html", {
            "course": course,
            "all_resources": all_resources,
            "related_courses": related_courses,
            "video": video,
        })
