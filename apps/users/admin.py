from django.contrib import admin
from .models import UserProfile


# Register your models here.

# 写一个管理器:命名, model+Admin
class UserProfileAdmin(admin.ModelAdmin):
    pass


# 将UserProfile注册到admin中，并且选择管理器为UserProfileAdmin
admin.site.register(UserProfile, UserProfileAdmin)
