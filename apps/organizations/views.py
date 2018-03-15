from django.shortcuts import render
from django.views.generic import View
from .models import CourseOrg, CityDict


# Create your views here.

class OrgView(View):
    def get(self, request):
        orgs = CourseOrg.objects.all()
        cities = CityDict.objects.all()
        org_total_num = orgs.count()
        return render(request, 'org-list.html', {
            'orgs': orgs,
            'cities': cities,
            'org_total_num': org_total_num,
        })
