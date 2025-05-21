"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

# noinspection PyUnresolvedReferences
from apps.photos.views import DefaultView,SettingsView,LoadView,GetAllInfoView

urlpatterns = [
    # �༭ͼƬ·��
    path('edit/', include('apps.photos.urls')),
    # Ĭ����Ϣ·��
    path('default/', DefaultView.as_view()),
    path('settings/', SettingsView.as_view()),
    path('loading/',LoadView.as_view()),
    path('getinfo/',GetAllInfoView.as_view())
]
