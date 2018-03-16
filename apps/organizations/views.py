from django.shortcuts import render
from django.views.generic import View
from .models import CourseOrg, CityDict
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.

class OrgView(View):
    def get(self, request):
        orgs = CourseOrg.objects.all()

        #热门的机构，排名后取前三个
        hot_orgs = orgs.order_by("-click_nums")[:3]

        cities = CityDict.objects.all()

        # 在前端选择城市，传到city_id，作为筛选，默认为空
        city_id = request.GET.get('city', '')
        # 如果city_id不是空，说明做了选择
        if city_id:
            orgs = orgs.filter(city_id=city_id)

        # 在前端选择组织类别，传到category，作为筛选，默认为空
        category = request.GET.get('ct','')
        if category:
            orgs = orgs.filter(category=category)

        # 由学习人数和课程数进行排序筛选
        sort = request.GET.get('sort','')
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
