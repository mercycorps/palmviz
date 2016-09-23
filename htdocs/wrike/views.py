import requests
import json
from django.core.urlresolvers import reverse_lazy
from django.conf import settings

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View

from django.contrib import messages

from .models import WrikeOauth2Credentials

class HomeView(TemplateView):
    template_name = 'wrike/home.html'


class WrikeOauth2SetupStep1(View):
    """
    Forwards the user to Wrike authorization URL to request an authorization code.
    After clicking on the URL, the user is redirected to the login page
    (if not already logged in) and then to a consent page to get confirmation approval.
    The consent page redirects the client to the redirect_uri with the code parameter
    set to the authorization code.
    """

    def get(self, request):
        oauth2_redirect_uri_part_one = reverse_lazy('oauth2redirect')
        hostname = request.META['HTTP_HOST']
        protocol = "https" if request.is_secure() else "http"
        oauth2_redirect_uri = '%s://%s%s' % (protocol, hostname, oauth2_redirect_uri_part_one)
        oauth2_authorization_uri  = 'https://www.wrike.com/oauth2/authorize?client_id=%s&response_type=code&redirect_uri=%s&scope=amReadOnlyGroup,wsReadOnly,amReadOnlyUser' %  (settings.WRIKE_OAUTH2_CLIENT_ID, oauth2_redirect_uri)
        return HttpResponseRedirect(oauth2_authorization_uri)



class WrikeOauthRedirectUriStep2(View):
    """
    Exchange authorization code obtained in Step1 for credentials (access_token and refresh_token)
    """
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
        result = requests.post(settings.WRIKE_ACCESS_TOKEN_URL, data=data, headers=headers)
        result_json = json.loads(result.text)

        if result_json.get("error", None) is None:
            defaults = {
                "access_token": result_json['access_token'],
                "refresh_token": result_json['refresh_token'],
                "token_type": result_json['token_type'],
            }
            cred, created = WrikeOauth2Credentials.objects.update_or_create(user=request.user, defaults=defaults)
        return HttpResponseRedirect(reverse_lazy('home'))




