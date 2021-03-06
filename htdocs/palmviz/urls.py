"""palmviz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views

from rest_framework import routers, serializers, viewsets

from views import schema_view, HomeView

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/docs/', schema_view),

    url(r'^login/$', views.login, name='login', kwargs={'template_name': '404.html'}),
    url(r'^logout/$', views.logout, name='logout', kwargs={'next_page': '/'}),

    url(r'^feedback/', include('feedback.urls')),
    url(r'^wrike/', include('wrike.urls')),
    url(r'^$', HomeView.as_view(), name='home'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
