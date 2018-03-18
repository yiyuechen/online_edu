# @Time    : 18-3-18
# @Author  : yiyue

from django.urls import path, re_path
from courses.views import CourseListView, CourseDetailView

app_name = 'courses'

urlpatterns = [
    path('list/', CourseListView.as_view(), name='course_list'),
    re_path('detail/(?P<course_id>\d+.*)/', CourseDetailView.as_view(),
            name='course_detail'),
]
