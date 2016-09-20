from django.conf.urls import include, url
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import TemplateView

from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

urlpatterns = [
    url(r'^setup/$', WrikeSetup.as_view(), name='wrike_setup'),
    #url(r'^pr/add/$', PurchaseRequestCreateView.as_view(), name='pr_new'),
    #url(r'^pr/edit/(?P<pk>\d+)/$', PurchaseRequestUpdateView.as_view(), name='pr_edit'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
