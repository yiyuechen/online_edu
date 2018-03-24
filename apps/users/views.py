from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from .models import UserProfile, EmailVerifyRecord
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from users.forms import UploadImageForm, UserInfoForm
import json


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
                    return render(request, 'index.html')
                else:
                    return render(request, 'login.html', {'msg': '你还未激活账户'})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误'})
        else:
            return render(request, 'login.html', {'login_form': login_form})


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
