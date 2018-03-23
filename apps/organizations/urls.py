# @Time    : 18-3-17
# @Author  : yiyue

from organizations.views import OrgView, AddUserAskView, OrgHomeView, \
    OrgCourseView, OrgDescView, OrgTeacherView, AddFavView, TeacherListView, \
    TeacherDetailView
from django.urls import path, re_path

app_name = 'organizations'

urlpatterns = [
    path('list/', OrgView.as_view(), name='org_list'),
    path('add_ask/', AddUserAskView.as_view(), name='add_ask'),
    re_path('home/(?P<org_id>\d+.*)/', OrgHomeView.as_view(), name='org_home'),
    re_path('course/(?P<org_id>\d+.*)/', OrgCourseView.as_view(),
            name='org_course'),
    re_path('desc/(?P<org_id>\d+.*)/', OrgDescView.as_view(), name='org_desc'),
    re_path('teacher/(?P<org_id>\d+.*)/', OrgTeacherView.as_view(),
            name='org_teacher'),

    path('teacher/list/', TeacherListView.as_view(), name='teacher_list'),

    re_path('teacher/detail/(?P<teacher_id>\d+.*)/', TeacherDetailView.as_view(), name='teacher_detail'),

    # 添加收藏
    path('add_fav/', AddFavView.as_view(), name='add_fav'),
]
