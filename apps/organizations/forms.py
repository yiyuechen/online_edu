# @Time    : 18-3-17
# @Author  : yiyue

from django import forms

from operation.models import UserAsk

import re


class UserAskForm(forms.ModelForm):
    # 这里可以添加自定义字段

    class Meta:
        # 使用UserAsk的model
        model = UserAsk
        # 通过一个列表指明需要哪几个字段
        fields = ['name', 'mobile', 'course_name']

    # 验证手机号码
    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        regex_mobile = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        p = re.compile(regex_mobile)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError(u"手机号码非法", code="mobile_invalid")
