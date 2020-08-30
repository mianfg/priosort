"""priosort URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf.urls import url, include
from django.urls import path

from priosort import views as views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^nuevo/', views.nuevo, name='nuevo'),
    url(r'^populate/', views.populate, name='populate'),
    path('<uuid:more>/', views.handle_uuid, name='handle_uuid'),
    path('<uuid:sorteo_id>/sortear', views.sortear, name='sortear'),
    path('eliminar-asignacion/<uuid:persona_id>', views.eliminar_asignacion, name='eliminar_asignacion'),
    path('post/asignacion', views.aniadir_asignacion, name='aniadir_asignacion'),
    path('post/nuevo', views.nuevo_sorteo, name='nuevo_sorteo'),
    path('admin/', admin.site.urls),
]
