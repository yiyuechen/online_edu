from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.urls import reverse

from .models import UserProfile, EmailVerifyRecord
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from users.forms import UploadImageForm, UserInfoForm
from operation.models import UserCourse, UserFavorite, UserMessage
import json
from organizations.models import CourseOrg, Teacher
from courses.models import Course
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from users.models import Banner


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(
                Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


# def user_login(request):
#     if request.method == "POST":
#         username = request.POST.get("username", "")
#         password = request.POST.get("password", "")
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return render(request, "index.html")
#         else:
#             return render(request, "login.html", {"msg": "用户名或密码错误"})
#     elif request.method == "GET":
#         return render(request, 'login.html', {})


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    # return render(request, 'index.html')
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, 'login.html', {'msg': '你还未激活账户'})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误'})
        else:
            return render(request, 'login.html', {'login_form': login_form})


class LogoutView(View):
    """user logout"""

    def get(self, request):
        logout(request)
        from django.urls import reverse
        return HttpResponseRedirect(reverse('index'))


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html',
                      {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            username = request.POST.get('email', '')
            if UserProfile.objects.filter(email=username):
                return render(request, 'register.html', {'msg': '此邮箱已经注册',
                                                         'register_form': register_form})
            password = request.POST.get('password', '')

            user_profile = UserProfile()
            user_profile.username = username
            user_profile.email = username
            user_profile.password = make_password(password)
            # 默认激活状态为false
            user_profile.is_active = False
            user_profile.save()

            # 写入欢迎消息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = "Welcome to our site."
            user_message.save()

            # 发送验证
            send_register_email(username, 'register')
            return render(request, 'login.html')
        else:
            return render(request, 'register.html',
                          {'register_form': register_form})


class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                # get the user obj with the right email. notice that userprofile is inherited
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, 'active_failure.html')
        return render(request, 'login.html', {'msg': '用户已激活'})


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, 'forgetpwd.html', {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            if send_register_email(email, send_type='forget'):
                return render(request, 'reset_passwd_mail.html')
            else:
                return render(request, 'forgetpwd.html',
                              {'forget_form': forget_form})
        else:
            return render(request, 'forgetpwd.html',
                          {'forget_form': forget_form})


class ResetView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, 'password_reset.html', {'email': email})
        else:
            return render(request, 'active_failure.html')


class ModifyPwdView(View):
    def post(self, request):
        modify_pwd_form = ModifyPwdForm(request.POST)

        if modify_pwd_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            if pwd1 != pwd2:
                return render(request, 'password_reset.html',
                              {'email': email, 'msg': '密码不一致'})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd1)
            user.save()
            return render(request, 'login.html', {'msg': '密码修改成功'})
        else:
            email = request.POST.get('email')
            return render(request, 'password_reset.html',
                          {'email': email, 'modify_form': modify_pwd_form})


class UserInfoView(LoginRequiredMixin, View):
    """用户个人中心"""

    def get(self, request):
        return render(request, 'usercenter-info.html', {

        })

    # instance指明哪个实例，否则会创建新的用户
    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse("{'status':'success'}",
                                content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors),
                                content_type='application/json')


class UploadImageView(LoginRequiredMixin, View):
    """上传头像"""

    # def post(self, request):
    #     image_form = UploadImageForm(request.POST, request.FILES)
    #     if image_form.is_valid():
    #         image = image_form.cleaned_data['image']
    #         request.user.image = image
    #         request.user.save()

    # 或者使用ModelForm的特性，用instance
    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES,
                                     instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return HttpResponse("{'status':'success'}",
                                content_type='application/json')
        else:
            return HttpResponse("{'status':'fail'}",
                                content_type='application/json')


class UpdatePwdView(View):
    """在个人中心修改密码"""

    def post(self, request):
        modify_pwd_form = ModifyPwdForm(request.POST)

        if modify_pwd_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return HttpResponse("{'status':'fail', 'msg':'密码不一致'}",
                                    content_type='application/json')
            user = request.user
            user.password = make_password(pwd1)
            user.save()
            return HttpResponse("{'status':'success'}",
                                content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_pwd_form.errors),
                                content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin, View):
    """发送改邮箱的验证码"""

    def get(self, request):
        email = request.GET.get('email', '')
        if UserProfile.objects.filter(email=email):
            return HttpResponse("{'email':'邮箱已存在'}",
                                content_type='application/json')
        send_register_email(email, 'update_email')
        return HttpResponse("{'status':'success'}",
                            content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    """修改邮箱"""

    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        existed_record = EmailVerifyRecord.objects.filter(email=email,
                                                          code=code,
                                                          send_type='update_email')
        if existed_record:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse("{'status':'success'}",
                                content_type='application/json')
        else:
            return HttpResponse("{'email':'验证码出错'}",
                                content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    """个人课程页面"""

    def get(self, request):
        my_courses = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter-mycourse.html', {
            'my_courses': my_courses,
        })


class MyFavOrgsView(LoginRequiredMixin, View):
    """个人收藏的机构"""

    def get(self, request):
        favs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        fav_org_list = []
        for fav in favs:
            org_id = fav.fav_id
            org = CourseOrg.objects.get(id=org_id)
            fav_org_list.append(org)

        return render(request, 'usercenter-fav-org.html', {
            'fav_org_list': fav_org_list,
        })


class MyFavTeachersView(LoginRequiredMixin, View):
    """个人收藏的教师"""

    def get(self, request):
        favs = UserFavorite.objects.filter(user=request.user, fav_type=3)
        fav_teacher_list = []
        for fav in favs:
            teacher_id = fav.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            fav_teacher_list.append(teacher)

        return render(request, 'usercenter-fav-teacher.html', {
            'fav_teacher_list': fav_teacher_list,
        })


class MyFavCoursesView(LoginRequiredMixin, View):
    """个人收藏的教师"""

    def get(self, request):
        favs = UserFavorite.objects.filter(user=request.user, fav_type=1)
        fav_course_list = []
        for fav in favs:
            course_id = fav.fav_id
            course = Course.objects.get(id=course_id)
            fav_course_list.append(course)

        return render(request, 'usercenter-fav-course.html', {
            'fav_course_list': fav_course_list,
        })


class MyMessageView(LoginRequiredMixin, View):
    """个人收藏的教师"""

    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)

        # 当用户点击消息喇叭后，清空所有未读消息
        all_unread_messages = UserMessage.objects.filter(user=request.user.id,
                                                         has_read=False)
        for message in all_unread_messages:
            message.has_read = True
            message.save()

        # 对消息进行分页
        # 尝试获取前台get请求传递过来的page参数
        # 如果是不合法的配置参数默认返回第一页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 这里指从allorg中取五个出来，每页显示5个
        p = Paginator(all_messages, 2, request=request)
        messages = p.page(page)

        return render(request, 'usercenter-message.html', {
            'messages': messages
        })


class IndexView(View):
    def get(self, request):
        # print(5/0)  #引起服务器错误，以便查看500页面
        # 上部分大尺寸轮播图
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False)[:5]
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs,
        })
