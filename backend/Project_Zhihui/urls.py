"""
URL configuration for Project_Zhihui project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # API v1 路由
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/user/', include('user.urls')),
    path('api/v1/organization/', include('organization.urls')),
    path('api/v1/project/', include('project.urls')),
    path('api/v1/studentproject/', include('studentproject.urls')),
    path('api/v1/projectscore/', include('projectscore.urls')),
    path('api/v1/pdf/', include('pdf_processing.urls')),
    path('api/v1/tag/', include('tag_db_writer.urls')),
    path('api/v1/search/', include('read_search.urls')),
    path('api/v1/notification/', include('notification.urls')),
    path('api/v1/dashboard/', include('dashboard.urls')),
    path('api/v1/agent/', include('agent.urls')),  # Python 版智能体
]

# 开发环境下提供静态文件和媒体文件服务
if settings.DEBUG:
    # 开发环境下，Django会自动处理STATICFILES_DIRS中的静态文件
    # 但为了确保admin静态文件正常工作，我们使用STATIC_ROOT
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
