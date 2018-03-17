# @Time    : 18-3-17
# @Author  : yiyue

from organizations.views import OrgView, AddUserAskView, OrgHomeView
from django.urls import path, re_path

app_name = 'organizations'

urlpatterns = [
    path('list/', OrgView.as_view(), name='org_list'),
    path('add_ask/', AddUserAskView.as_view(), name='add_ask'),
    re_path('home/(?P<org_id>\d+.*)/', OrgHomeView.as_view(), name='org_home')
]
