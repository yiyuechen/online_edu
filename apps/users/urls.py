# @Time    : 18-3-23
# @Author  : yiyue

from django.urls import path, re_path
from users.views import UserInfoView, UploadImageView, UpdatePwdView
from users.views import SendEmailCodeView, UpdateEmailView, MyCourseView
from users.views import MyFavOrgsView, MyFavTeachersView, MyFavCoursesView, \
    MyMessageView

app_name = 'users'

urlpatterns = [
    # user info
    path('user_info/', UserInfoView.as_view(), name='user_info'),
    # upload user avatar
    path('image/upload/', UploadImageView.as_view(), name="image_upload"),
    # update user password in user center
    path('update/pwd/', UpdatePwdView.as_view(), name="update_pwd"),
    # send code to reset email
    path('send_email_code/', SendEmailCodeView.as_view(),
         name="send_email_code"),
    # send code to reset email
    path('update_email/', UpdateEmailView.as_view(),
         name="update_email"),
    path('mycourse/', MyCourseView.as_view(),
         name="mycourse"),
    path('myfav/org/', MyFavOrgsView.as_view(),
         name="fav_org"),
    path('myfav/teacher/', MyFavTeachersView.as_view(),
         name="fav_teacher"),
    path('myfav/course/', MyFavCoursesView.as_view(),
         name="fav_course"),
    path('mymessage/', MyMessageView.as_view(),
         name="mymessage"),
]
