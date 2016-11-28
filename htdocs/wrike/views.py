import requests
import json
import operator
import logging

from django.core.urlresolvers import reverse_lazy
from django.conf import settings

from django.db.models import Count, F, FloatField, Sum

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View

from django.contrib import messages

from .models import WrikeOauth2Credentials, Folder

logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    template_name = 'wrike/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        gen_tech_tasks = get_palm_general_tech_support_by_countries()
        countries = get_countries()
        recruitments = get_palm_recruiting_data()
        data = {}
        countries_in_gen_tech = []


        for task in gen_tech_tasks:
            country = task['Country']
            countries_in_gen_tech.append(country)
            data[country] = {"gen_tech": task['Num_Tasks']}

        for c in countries:
            num_recs = recruitments.filter(parents=c).count()
            country = c.title
            if country in countries_in_gen_tech:
                data[country]["recruitment"] = num_recs
            else:
                if num_recs > 0:
                    data[country] = {"gen_tech": 0, "recruitment": num_recs}

        sorted_data = sorted(data.items(), key=operator.itemgetter(0))
        categories = []

        gen_tech = []
        recs = []
        for bar in sorted_data:
            country = bar[0]
            categories.append(country)
            wrike_categories = bar[1]
            #print(bar)
            gen_tech.append(wrike_categories.get("gen_tech"))
            recs.append(wrike_categories.get("recruitment"))

        series = [
            {"name": "General Tech Support", "data": gen_tech},
            {"name": "Recruitments", "data": recs}
        ]
        context['categories'] = json.dumps(categories)
        context['data'] = json.dumps(series)
        return context

def get_countries():
    return Folder.objects.filter(parents=settings.WRIKE_PALM_COUNTRIES_FOLDER_ID).order_by('title')


def get_material_aid_data():
    filters = {

    }
    countries = get_countries()
    data = Folder.objects.filter(parents=settings.WRIKE_PALM_MATERIAL_AID_FOLDER_ID).filter(parents__in=countries)
    return data


def get_palm_general_tech_support_by_countries():
    """
    Returns number of tasks by country in the PALM General Tech Support folder.
    """
    filters = {
        "tasks__folders__id": settings.WRIKE_PALM_GENERAL_TECH_SUPPORT_FOLDER_ID
    }
    tasks_by_country = Folder.objects.get(pk=settings.WRIKE_PALM_COUNTRIES_FOLDER_ID).subfolders\
                        .filter(tasks__folders__id=settings.WRIKE_PALM_GENERAL_TECH_SUPPORT_FOLDER_ID)\
                        .distinct()\
                        .annotate(Country=F('title'), Num_Tasks=Count('tasks'))\
                        .values('Country', 'Num_Tasks')\
                        .order_by('Country')

    return tasks_by_country

def get_palm_recruiting_data():
    countries = get_countries()
    recruitments = Folder.objects.filter(parents=settings.WRIKE_PALM_RECRUITING_FOLDER_ID).filter(parents__in=countries)
    #Folder.objects.filter(parents=settings.WRIKE_PALM_RECRUITING_FOLDER_ID).fer(parents=iq)
    return recruitments



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
            logger.warn("WrikeOauth2Credentials object is creatd. right? %s" % created)
        return HttpResponseRedirect(reverse_lazy('home'))




