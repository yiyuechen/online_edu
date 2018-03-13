# @Time    : 18-3-9
# @Author  : yiyue

from django import forms
# from django.shortcuts import render
# from django.contrib.auth import authenticate, login
from captcha.fields import CaptchaField


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


class RegisterForm(forms.Form):
    email=forms.EmailField(required=True)
    password=forms.CharField(required=True, min_length=5)
    captcha = CaptchaField()