import operator

from django.db.models import Q, Count, F, FloatField, Sum
from django.conf import settings

from .models import *

def get_support_data_by_country(criteria):
    gen_tech_tasks = get_palm_general_tech_support_by_countries(criteria)
    countries = get_countries()
    recruitments = get_palm_recruiting_data(countries, criteria)
    material_aid_projects = get_material_aid_data(countries, criteria)
    tdy_projects = get_short_term_tdy_data(countries, criteria)
    agency_response_projects = get_agency_response_data(countries, criteria)
    field_trips_data = get_field_trips_data(countries, criteria)
    shipping_n_logistics_projects = get_shipping_n_logistics_projects(countries, criteria)
    tenders_projects = get_tenders_data(countries, criteria)

    # dictionary to hold data in the format expected by the hicharts stacked bar chart
    data = {}

    # Add Tasks count by country to the data dictionary.
    for task in gen_tech_tasks:
        country = task['Country']
        data[country] = {"gen_tech": task['Num_Tasks']}

    # For each country, sum the total number of projects by type and add to the data dic.
    for c in countries:
        country = c.title
        num_recs = recruitments.filter(parents=c).count()
        num_material_aid_projects = material_aid_projects.filter(parents=c).count()
        num_tdy_projects = tdy_projects.filter(parents=c).count()
        num_agency_response_projects = agency_response_projects.filter(parents=c).count()
        num_field_trips_data = field_trips_data.filter(parents=c).count()
        num_shipping_n_logistics_projects = shipping_n_logistics_projects.filter(parents=c).count()
        num_tenders_projects = tenders_projects.filter(parents=c).count()

        # Check whether the data dic already has gen_tasks for this country.
        if data.get(country, None) is None:
            # Apparently, there are no gen_tasks for this country in the main data dic.
            # Now check if there is data in any other category for this country and if there is
            # then initiate an empty subdictionary for this country in the main data dic.
            if num_recs > 0 or num_material_aid_projects > 0 or num_tdy_projects > 0\
                    or num_agency_response_projects > 0 or num_field_trips_data > 0\
                    or num_shipping_n_logistics_projects > 0\
                    or num_tenders_projects > 0:
                        data[country] = {}
            else:
                # At this point, there is no data for this country in any category so skip.
                continue

        # Add data for each category to this country in the main data dic.
        data[country]["recruitment"] = num_recs
        data[country]["material_aid"] = num_material_aid_projects
        data[country]["tdy"] = num_tdy_projects
        data[country]["agency_response"] = num_agency_response_projects
        data[country]["field_trips"] = num_field_trips_data
        data[country]["snl"] = num_shipping_n_logistics_projects
        data[country]["tenders"] = num_tenders_projects

    # Sort the main data dic by Country in asc order.
    sorted_data = sorted(data.items(), key=operator.itemgetter(0))


    y_axis_labels = []
    gen_tech_list = []
    recruitments_list = []
    material_aid_list = []
    tdys_list = []
    agency_responses_list = []
    field_trips_list = []
    shipping_n_logistics_list = []
    tenders_list = []

    # Loop through the sorted data and populate a list of data points for each
    # supporty category in a format that the hicharts stacked bar chart expects
    for bar in sorted_data:
        country = bar[0]
        y_axis_labels.append(country)
        series_names = bar[1]
        gen_tech_list.append(series_names.get("gen_tech", "0"))
        recruitments_list.append(series_names.get("recruitment", "0"))
        material_aid_list.append(series_names.get("material_aid", "0"))
        tdys_list.append(series_names.get("tdy", "0"))
        agency_responses_list.append(series_names.get("agency_response", "0"))
        field_trips_list.append(series_names.get("field_trips", "0"))
        shipping_n_logistics_list.append(series_names.get("snl", "0"))
        tenders_list.append(series_names.get("tenders", "0"))

    # Final list of dictionaries for the hichart stacked bar chart.
    series = [
        {"name": "General Tech Support", "data": gen_tech_list},
        {"name": "Recruitments", "data": recruitments_list},
        {"name": "Material Aid", "data": material_aid_list},
        {"name": "Short-term TDYs", "data": tdys_list},
        {"name": "Agency Responses", "data": agency_responses_list},
        {"name": "Field Trips", "data": field_trips_list},
        {"name": "Shipping and Logistics", "data": shipping_n_logistics_list},
        {"name": "Tenders", "data": tenders_list},
    ]
    return (y_axis_labels, series)

def get_countries():
    return Folder.objects\
        .filter(parents=settings.WRIKE_PALM_COUNTRIES_FOLDER_ID)\
        .order_by('title')


def get_tenders_data(countries=None, criteria=None):
    if countries is None: countries = get_countries()
    filters = get_completed_date_filter(None, criteria)
    data = Folder.objects\
        .filter(Q(parents=settings.WRIKE_PALM_TENDERS_FOLDER_ID)|\
                Q(parents=settings.WRIKE_PALM_TENDERS_ARCHIVE_FOLDER_ID))\
        .filter(**filters)\
        .filter(parents__in=countries)
    return data


def get_shipping_n_logistics_projects(countries=None, criteria=None):
    if countries is None: countries = get_countries()
    filters = get_completed_date_filter(None, criteria)
    data = Folder.objects\
        .filter(Q(parents=settings.WRIKE_PALM_SHIPPING_LOGISTICS_FOLDER_ID)|\
                Q(parents=settings.WRIKE_PALM_SHIPPING_LOGISTICS_ARCHIVE_FOLDER_ID))\
        .filter(**filters)\
        .filter(parents__in=countries)
    return data


def get_field_trips_data(countries=None, criteria=None):
    if countries is None: countries = get_countries()
    filters = get_completed_date_filter(None, criteria)
    data = Folder.objects\
        .filter(Q(parents=settings.WRIKE_PALM_FILED_TRIPS_FOLDER_ID)|\
                Q(parents=settings.WRIKE_PALM_FIELD_TRIPS_ARCHIVE_FOLDER_ID))\
        .filter(**filters)\
        .filter(parents__in=countries)
    return data


def get_agency_response_data(countries=None, criteria=None):
    if countries is None: countries = get_countries()
    filters = get_completed_date_filter(None, criteria)
    data = Folder.objects\
        .filter(Q(parents=settings.WRIKE_PALM_AGENCY_RESPONSE_FOLDER_ID)|\
                Q(parents=settings.WRIKE_PALM_AGENCY_RESPONSE_ARCHIVE_FOLDER_ID))\
        .filter(**filters)\
        .filter(parents__in=countries)
    return data


def get_short_term_tdy_data(countries=None, criteria=None):
    if countries is None: countries = get_countries()
    filters = get_completed_date_filter(None, criteria)
    data = Folder.objects\
        .filter(Q(parents=settings.WRIKE_PALM_SHORT_TERM_TDY_FOLDER_ID) |\
                 Q(parents=settings.WRIKE_PALM_SHORT_TERM_TDY_ARCHIVE_FOLDER_ID))\
        .filter(**filters)\
        .filter(parents__in=countries)
    return data


def get_material_aid_data(countries=None, criteria=None):
    if countries is None: countries = get_countries()
    filters = get_completed_date_filter(None, criteria)
    data = Folder.objects\
        .filter(Q(parents=settings.WRIKE_PALM_MATERIAL_AID_FOLDER_ID)|\
                Q(parents=settings.WRIKE_PALM_MATERIAL_AID_ARCHIVE_FOLDER_ID))\
        .filter(**filters)\
        .filter(parents__in=countries)
    return data


def get_palm_recruiting_data(countries=None, criteria=None):
    if countries is None: countries = get_countries()

    filters = get_completed_date_filter(None, criteria)
    recruitments = Folder.objects\
        .filter(Q(parents=settings.WRIKE_PALM_RECRUITING_FOLDER_ID) |\
                 Q(parents=settings.WRIKE_PALM_RECRUITMENT_ARCHIVE_FOLDER_ID))\
        .filter(**filters)\
        .filter(parents__in=countries)
    return recruitments


def get_palm_general_tech_support_by_countries(criteria):
    """
    Returns number of tasks by country in the PALM General Tech Support folder.
    """
    filtering = {"tasks__folders__id": settings.WRIKE_PALM_GENERAL_TECH_SUPPORT_FOLDER_ID}
    filtering.update(get_completed_date_filter("tasks__", criteria))
    tasks_by_country = Folder.objects.get(pk=settings.WRIKE_PALM_COUNTRIES_FOLDER_ID).subfolders\
                        .filter(**filtering)\
                        .distinct()\
                        .annotate(Country=F('title'), Num_Tasks=Count('tasks'))\
                        .values('Country', 'Num_Tasks')\
                        .order_by('Country')

    return tasks_by_country


def get_completed_date_filter(prefix, criteria):
    filters = {}
    start = criteria.get('start', None)
    end = criteria.get('end', None)
    if prefix == None: prefix = ''
    if start:
        filters['%scompletedDate__gte' % prefix] = start
    if end:
        filters['%scompletedDate__lte' % prefix] = end
    return filters