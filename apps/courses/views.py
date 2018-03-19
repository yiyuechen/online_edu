from django.shortcuts import render
from django.views.generic import View
from courses.models import Course, CourseResource

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from operation.models import UserFavorite


class CourseListView(View):
    def get(self, request):
        courses = Course.objects.all().order_by("-add_time")
        # 右侧栏热门课程
        hot_courses = Course.objects.all().order_by("-click_nums")[:3]

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
                has_fav_course =True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id,
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


class CourseInfoView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)
        course_resource = CourseResource.objects.filter(course=course)
        # ?
        # course_resource = CourseResource.objects.get(id=course_id)
        return render(request, 'course-video.html',{
            'course': course,
            'course_resource': course_resource
        })
