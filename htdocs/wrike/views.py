import requests
import json
from django.core.urlresolvers import reverse_lazy
from django.conf import settings

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View

# Create your views here.
class WrikeSetup(View):

    _client_secret = '6QOQFsSMaLVlKG9ciMmQIPYjMzrqPlogVLojgVzsEaQww5MJ8bL7sWjgLUWcgIdk'

    def get(self, request):
        oauth2_redirect_uri_part_one = reverse_lazy('oauth2redirect')
        hostname = request.META['HTTP_HOST']
        protocol = "https" if request.is_secure() else "http"
        oauth2_redirect_uri = '%s://%s%s' % (protocol, hostname, oauth2_redirect_uri_part_one)
        oauth2_authorization_uri  = 'https://www.wrike.com/oauth2/authorize?client_id=%s&response_type=code&redirect_uri=%s&scope=amReadOnlyGroup,wsReadOnly,amReadOnlyUser' %  (settings.WRIKE_OAUTH2_CLIENT_ID, oauth2_redirect_uri)
        return HttpResponseRedirect(oauth2_authorization_uri)



class WrikeOauthRedirectURI(View):
    _wrike_token_url = "https://www.wrike.com/oauth2/token"

    def get(self, request):
        oauth2_redirect_uri_part_one = reverse_lazy('oauth2redirect')
        hostname = request.META['HTTP_HOST']
        protocol = "https" if request.is_secure() else "http"
        oauth2_redirect_uri = '%s://%s%s' % (protocol, hostname, oauth2_redirect_uri_part_one)

        data = {
            "client_id": settings.WRIKE_OAUTH2_CLIENT_ID,
            "client_secret": settings.WRIKE_OAUTH2_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": request.GET.get("code"),
            "redirect_uri": oauth2_redirect_uri,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'} #{'Content-Type': 'application/json'}
        result = requests.post(self._wrike_token_url, data=data, headers=headers)
        print(result.text)
        d = json.loads(result.text)
        return HttpResponse("%s-%s" % (d['error'], d['error_description']))