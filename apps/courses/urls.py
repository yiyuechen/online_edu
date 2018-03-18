# @Time    : 18-3-18
# @Author  : yiyue

from django.urls import path, re_path
from courses.views import CourseListView

app_name = 'courses'

urlpatterns = [
    path('list/', CourseListView.as_view(), name='course_list'),
]