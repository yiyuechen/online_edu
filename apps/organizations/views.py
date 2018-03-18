from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from .models import CourseOrg, CityDict
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from .forms import UserAskForm
from operation.models import UserFavorite


# Create your views here.

class OrgView(View):
    def get(self, request):
        orgs = CourseOrg.objects.all()

        # 热门的机构，排名后取前三个
        hot_orgs = orgs.order_by("-click_nums")[:3]

        cities = CityDict.objects.all()

        # 在前端选择城市，传到city_id，作为筛选，默认为空
        city_id = request.GET.get('city', '')
        # 如果city_id不是空，说明做了选择
        if city_id:
            orgs = orgs.filter(city_id=city_id)

        # 在前端选择组织类别，传到category，作为筛选，默认为空
        category = request.GET.get('ct', '')
        if category:
            orgs = orgs.filter(category=category)

        # 由学习人数和课程数进行排序筛选
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                orgs = orgs.order_by("-students")
            elif sort == 'courses':
                orgs = orgs.order_by("-course_nums")

        # 完成筛选之后，再统计
        org_total_num = orgs.count()

        # 对课程机构进行分页
        # 尝试获取前台get请求传递过来的page参数
        # 如果是不合法的配置参数默认返回第一页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 这里指从allorg中取五个出来，每页显示5个
        p = Paginator(orgs, 2, request=request)
        orgs = p.page(page)

        return render(request, 'org-list.html', {
            'orgs': orgs,
            'cities': cities,
            'org_total_num': org_total_num,
            'city_id': city_id,
            'category': category,
            'hot_orgs': hot_orgs,
            'sort': sort
        })


class AddUserAskView(View):
    def post(self, request):
        user_ask_form = UserAskForm(request.POST)
        if user_ask_form.is_valid():
            # 当commit为true进行真正保存
            user_ask = user_ask_form.save(commit=True)
            # 如果保存成功,则返回json字符串为sucess,后面content type是告诉浏览器信息类型
            return HttpResponse("{'status': 'success', 'msg':'添加成功'}",
                                content_type='application/json')
        else:
            return HttpResponse("{'status':'fail', 'msg':'添加出错'}",
                                content_type='application/json')


class OrgHomeView(View):
    """机构首页"""

    def get(self, request, org_id):
        current_page = 'home'
        course_org = CourseOrg.objects.get(id=int(org_id))
        courses = course_org.course_set.all()[:3]
        teachers = course_org.teacher_set.all()[:1]

        # 判断用户是否收藏
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user,
                                           fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-homepage.html', {
            'courses': courses,
            'teachers': teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav
        })


class OrgCourseView(View):
    """机构课程页"""

    def get(self, request, org_id):
        current_page = 'course'
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 因为是课程页，取出全部课程
        courses = course_org.course_set.all()

        # 判断用户是否收藏
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user,
                                           fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-course.html', {
            'courses': courses,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgDescView(View):
    """机构详情页"""

    def get(self, request, org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))

        # 判断用户是否收藏
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user,
                                           fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav
        })


class OrgTeacherView(View):

    def get(self, request, org_id):
        current_page = 'teachers'
        course_org = CourseOrg.objects.get(id=int(org_id))
        teachers = course_org.teacher_set.all()

        # 判断用户是否收藏
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user,
                                           fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-teachers.html', {
            'course_org': course_org,
            'current_page': current_page,
            'teachers': teachers,
            'has_fav': has_fav
        })


class AddFavView(View):
    """用户收藏，可以是课程，机构和讲师，也可以是撤销收藏"""

    def post(self, request):
        # 默认值为0
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)

        # 判断是否登录，没登录，则是匿名的user类
        if not request.user.is_authenticated:
            # 返回错误信息给ajax， 跳转到登录页面在ajax中再实现
            return HttpResponse("{'status':'fail', 'msg':'用户未登录'}",
                                content_type='application/json')
        existing_records = UserFavorite.objects.filter(
            user=request.user,
            fav_id=int(fav_id),
            fav_type=int(fav_type),
        )
        if existing_records:
            # 如果收藏已经存在，就取消收藏
            existing_records.delete()
            return HttpResponse("{'status':'success', 'msg':'收藏'}",
                                content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()
                return HttpResponse("{'status':'success', 'msg':'已收藏'}",
                                    content_type='application/json')
            else:
                return HttpResponse("{'status':'fail', 'msg':'收藏出错'}",
                                    content_type='application/json')
