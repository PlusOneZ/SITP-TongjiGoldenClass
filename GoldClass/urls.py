"""GoldClass URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from CourseView.views import *
from TaskView.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view, name='index'),
    path('signin/', sign_in_view, name='sign_in'),
    path('login/', login_view, name='login'),
    path('me/', console_view, name='console'),
    path('tasks/', task_list_view, name='tasks'),
    path('courses/', courses_list_view, name='courses'),
    path('courses/<int:index>', course_view, name='course'),
    path('tasks/<int:index>', task_view, name='course'),
    path(r'onlineLecture/', in_develop, name='lectures'),
    path(r'courseRecords/', in_develop, name='records')
]
