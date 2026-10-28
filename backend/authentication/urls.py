from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    # 发送验证码
    path('send-email-code/', views.send_email_code, name='send_email_code'),
    
    # 认证相关接口
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),  # 统一登录接口
    path('logout/', views.logout, name='logout'),
    path('verify/', views.verify, name='verify'),
    path('refresh/', views.refresh, name='refresh'),
    
    # 密码相关
    path('password/', views.change_password, name='change_password'),
    path('reset/', views.reset_password_request, name='reset_password_request'),
    path('reset/confirm/', views.reset_password, name='reset_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    
    # 邮箱相关
    path('change_email/', views.change_email, name='change_email'),
    
    # 登录日志
    path('login-logs/', views.login_logs, name='login_logs'),
    
    # 验证码验证
    path('verify-code/', views.verify_email_code_view, name='verify_email_code'),
    
    # 用户存在性检查
    path('check-email/', views.check_email_exists, name='check_email_exists'),
    path('check-username/', views.check_username_exists, name='check_username_exists'),
    
    # 账户注销相关
    path('delete-account/request/', views.request_account_deletion, name='request_account_deletion'),
    path('delete-account/cancel/', views.cancel_account_deletion, name='cancel_account_deletion'),
    path('delete-account/status/', views.account_deletion_status, name='account_deletion_status'),
]