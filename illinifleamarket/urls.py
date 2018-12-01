"""illinifleamarket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls import url
from market import views as views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name = 'home'),
    url(r'^add/', views.item_create, name='item_create'),
    url(r'^delete/(?P<id>.*)', views.item_delete, name='item_delete'),
    url(r'^update/(?P<id>.*)', views.item_update, name='item_update'),
    url(r'^search/', views.item_search, name='item_search'),

    url(r'^login/', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^MyItems/$', views.MyItems, name='MyItems'),

    url(r'^profile_update/$', views.profile_update, name='profile_update'),
    url(r'^pwdchange/$', views.pwd_change, name='pwd_change'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^detail/(?P<id>.*)', views.item_detail, name='item_detail'),
    url(r'^confirm/$', views.user_confirm),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
