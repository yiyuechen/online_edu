"""mooc_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf.urls import include
# from users.views import user_login
import xadmin
from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, \
    ResetView, ModifyPwdView, LogoutView
from organizations.views import OrgView
from .settings import MEDIA_ROOT

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name="index"),
    # path('login/', user_login, name='login'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('captcha/', include('captcha.urls')),
    re_path('active/(?P<active_code>.*)/', ActiveUserView.as_view(),
            name='user_active'),
    path('forget/', ForgetPwdView.as_view(), name='forget_pwd'),
    re_path('reset/(?P<active_code>.*)/', ResetView.as_view(),
            name='reset_pwd'),
    path('modify/', ModifyPwdView.as_view(), name='modify_pwd'),

    # 包含机构列表页
    path('org/', include('organizations.urls', namespace='organizations')),

    # 包含课程列表页
    path('course/', include('courses.urls', namespace='courses')),

    # 用户信息页面
    path('users/', include('users.urls', namespace='users')),

    # 配置上传文件图片的处理
    # re_path('media/(?P<path>.*)/', serve, {'document_root': MEDIA_ROOT}),
    re_path(r'^media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),
]
