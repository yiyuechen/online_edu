# @Time    : 18-3-23
# @Author  : yiyue

from django.urls import path, re_path
from users.views import UserInfoView, UploadImageView, UpdatePwdView

app_name = 'users'

urlpatterns = [
    path('user_info/', UserInfoView.as_view(), name='user_info'),
    path('image/upload/', UploadImageView.as_view(), name="image_upload"),
    path('update/pwd/', UpdatePwdView.as_view(), name="update_pwd"),
]
