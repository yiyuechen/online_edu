from django.shortcuts import render
from django.views.generic import View
from courses.models import Course

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

class CourseListView(View):
    def get(self, request):
        courses = Course.objects.all()

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
            'courses': courses
        })
