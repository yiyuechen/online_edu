# @Time    : 18-3-11
# @Author  : yiyue

from random import Random
from users.models import EmailVerifyRecord

from django.core.mail import send_mail
from mooc_project.settings import EMAIL_FROM


def random_str(random_length=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        str += chars[random.randint(0, length)]
    return str


def send_register_email(email, send_type='register'):
    # 发送之前先保存到数据库，以便查询链接是否存在
    # 实例化一个EmailVerifyRecord对象
    email_record = EmailVerifyRecord()
    code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type

    email_record.save()

    # 定义邮件内容
    email_title = ''
    email_body = ''

    if send_type == "register":
        email_title = "localhost_mooc注册激活链接"
        email_body = "请点击下面的链接激活你的账号: http://127.0.0.1:8000/active/{0}".format(
            code)

    elif send_type == 'forget':
        email_title = "localhost_mooc找回密码链接"
        email_body = "请点击下面的链接找回你的密码: http://127.0.0.1:8000/reset/{0}".format(
            code)

    elif send_type == 'update_email':
        email_title = "localhost_mooc修改邮箱"
        email_body = "邮箱验证码为: {0}".format(code)


    else:
        return False
    # 使用Django内置函数完成邮件发送。四个参数：主题，邮件内容，从哪里发，接受者list
    send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    # 如果发送成功
    if send_status:
        return True
