import xadmin

from .models import EmailVerifyRecord, Banner


# 创建admin的管理类，继承object
class EmailVerifyRecordAdmin(object):
    # 默认需要显示的列，点击邮箱验证码显示
    list_display = ['code', 'email', 'send_type', 'send_time']
    # 搜索字段
    search_fields = ['code', 'email', 'send_type']
    # pass
    # 配置筛选字段
    list_filter = ['code', 'email', 'send_type', 'send_time']


class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
