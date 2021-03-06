from django.conf.urls import include, url
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import TemplateView

from rest_framework.urlpatterns import format_suffix_patterns

from wrike.views import *

urlpatterns = [
    url(r'^setup/$', WrikeOauth2SetupStep1.as_view(), name='wrike_setup'),
    url(r'^oauth2_redirect/$', WrikeOauthRedirectUriStep2.as_view(), name='oauth2redirect'),
    url(r'^support_by_country/$', SupportByCountry.as_view(), name='support_by_country'),
    url(r'^support_by_region/$', SupportByRegion.as_view(), name='support_by_region'),
    url(r'^support_by_person/$', SupportCompletedByPerson.as_view(), name='support_by_person'),
    #url(r'^pr/edit/(?P<pk>\d+)/$', PurchaseRequestUpdateView.as_view(), name='pr_edit'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
