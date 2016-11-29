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
        recruitments = get_palm_recruiting_data(countries)
        material_aid_projects = get_material_aid_data(countries)
        tdy_projects = get_short_term_tdy_data(countries)
        agency_response_projects = get_agency_response_data(countries)
        field_trips_data = get_field_trips_data(countries)

        data = {}
        countries_in_gen_tech = []


        for task in gen_tech_tasks:
            country = task['Country']
            countries_in_gen_tech.append(country)
            data[country] = {"gen_tech": task['Num_Tasks']}

        for c in countries:
            country = c.title
            num_recs = recruitments.filter(parents=c).count()
            num_material_aid_projects = material_aid_projects.filter(parents=c).count()
            num_tdy_projects = tdy_projects.filter(parents=c).count()
            num_agency_response_projects = agency_response_projects.filter(parents=c).count()
            num_field_trips_data = field_trips_data.filter(parents=c).count()

            if country in countries_in_gen_tech:
                data[country]["recruitment"] = num_recs
                data[country]["material_aid"] = num_material_aid_projects
                data[country]["tdy"] = num_tdy_projects
                data[country]["agency_response"] = num_agency_response_projects
                data[country]["field_trips"] = num_field_trips_data
            else:
                if num_recs > 0:
                    countries_in_gen_tech.append(country)
                    data[country] = {"recruitment": num_recs}

                if num_material_aid_projects > 0:
                    countries_in_gen_tech.append(country)
                    data[country] = {"material_aid": num_material_aid_projects}

                if num_tdy_projects > 0:
                    countries_in_gen_tech.append(country)
                    data[country] = {"tdy": num_tdy_projects}

                if num_agency_response_projects > 0:
                    countries_in_gen_tech.append(country)
                    data[country] = {"agency_response": num_agency_response_projects}

                if num_field_trips_data > 0:
                    countries_in_gen_tech.append(country)
                    data[country] = {"field_trips": num_field_trips_data}

        sorted_data = sorted(data.items(), key=operator.itemgetter(0))
        categories = []

        gen_tech = []
        recs = []
        material_aid = []
        tdys = []
        agency_responses = []
        field_trips = []

        for bar in sorted_data:
            country = bar[0]
            categories.append(country)
            wrike_categories = bar[1]
            #print(bar)
            gen_tech.append(wrike_categories.get("gen_tech", "0"))
            recs.append(wrike_categories.get("recruitment", "0"))
            material_aid.append(wrike_categories.get("material_aid", "0"))
            tdys.append(wrike_categories.get("tdy", "0"))
            agency_responses.append(wrike_categories.get("agency_response", "0"))
            field_trips.append(wrike_categories.get("field_trips", "0"))

        series = [
            {"name": "General Tech Support", "data": gen_tech},
            {"name": "Recruitments", "data": recs},
            {"name": "Material Aid", "data": material_aid},
            {"name": "Short-term TDYs", "data": tdys},
            {"name": "Agency Responses", "data": agency_responses},
            {"name": "Field Trips", "data": field_trips},
        ]
        context['categories'] = json.dumps(categories)
        context['data'] = json.dumps(series)
        return context

def get_countries():
    return Folder.objects.filter(parents=settings.WRIKE_PALM_COUNTRIES_FOLDER_ID).order_by('title')


def get_field_trips_data(countries=None):
    if countries is None: countries = get_countries()
    data = Folder.objects.filter(parents=settings.WRIKE_PALM_FILED_TRIPS_FOLDER_ID).filter(parents__in=countries)
    return data


def get_agency_response_data(countries=None):
    if countries is None: countries = get_countries()
    data = Folder.objects.filter(parents=settings.WRIKE_PALM_AGENCY_RESPONSE_FOLDER_ID).filter(parents__in=countries)
    return data


def get_short_term_tdy_data(countries=None):
    if countries is None: countries = get_countries()
    data = Folder.objects.filter(parents=settings.WRIKE_PALM_SHORT_TERM_TDY_FOLDER_ID).filter(parents__in=countries)
    return data


def get_material_aid_data(countries=None):
    if countries is None: countries = get_countries()
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

def get_palm_recruiting_data(countries=None):
    if countries is None: countries = get_countries()
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




