from django.shortcuts import render
from django.views.generic import View
from courses.models import Course

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger


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
        return render(request, 'course-detail.html', {
            'course': course,
        })