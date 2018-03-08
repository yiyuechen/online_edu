import xadmin

from .models import EmailVerifyRecord, Banner
from xadmin import views


# 创建X admin的全局管理器并与view绑定
class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


# xadmin 全局配置
class GlobalSettings(object):
    site_title = "Vic's 后台管理"
    site_footer = "Vic"
    # 收起左侧菜单
    menu_style = "accordion"


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
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
