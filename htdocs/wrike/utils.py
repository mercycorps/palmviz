import datetime
import requests
import json
import logging
import pytz

from django.conf import settings
from django.apps import apps

from django.utils import timezone
from django.utils.timezone import utc
from django.utils.encoding import smart_text

from django.contrib.auth.models import User

from .models import WrikeOauth2Credentials, CustomField, Contact, Folder, Task, CustomFieldTask

logger = logging.getLogger(__name__)
mail_logger = logging.getLogger('app_admins')

def get_wrike_access_token():
    """
    If the access token is older than one hour, then fetch a new one since
    they get expired after one hour.
    """
    user = User.objects.get(username=settings.WRIKE_API_USER_ACCOUNT)
    cred = WrikeOauth2Credentials.objects.get_or_none(pk=user.pk)
    if cred:
        now_utc = datetime.datetime.utcnow().replace(tzinfo=utc)
        diff = now_utc - cred.last_time_access_token_fetched
        # if it has been more than 59 minutes, get a new access_token
        if diff.seconds >= 3540:
            data = {
                "client_id": settings.WRIKE_OAUTH2_CLIENT_ID,
                "client_secret": settings.WRIKE_OAUTH2_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": cred.refresh_token
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'} #{'Content-Type': 'application/json'}
            result = requests.post(settings.WRIKE_ACCESS_TOKEN_URL, data=data, headers=headers)
            result_json = json.loads(result.text)

            if result_json.get("error", None) is None:
                defaults = {
                    "access_token": result_json['access_token'],
                }
                cred.access_token = result_json['access_token']
                cred.save()
        return cred.access_token
    return None



def get_model_fields_names(model_name):
    model = apps.get_model(app_label='wrike', model_name=model_name)
    cols = model._meta.get_fields()
    col_names = []
    for col in cols:
        col_names.append(col.name)
    return col_names


def process_wrike_data():
    if process_wrike_custom_fields() == False:
        mail_logger.error("notifiy adming")

    if process_wrike_contacts() == False:
        mail_logger.error("notify admins")

    if process_wrike_folders() == False:
        mail_logger.error("notify admins")

    if process_wrike_tasks() == False:
        mail_logger.error("notify admins")


def process_wrike_custom_fields():
    """
    Fetches custom_fields from Wrike's Mercy Corps account and stores them.
    """
    try:
        access_token = get_wrike_access_token()
        headers = {"Authorization": "bearer %s" % access_token}
        custom_fields = requests.get(settings.WRIKE_CUSTOMFIELDS_API_URL, headers=headers)
        custom_fields_json = json.loads(custom_fields.text)
    except Exception as e:
        logger.error(e)
        return False

    db_col_names = get_model_fields_names('CustomField')

    try:
        data = custom_fields_json['data'][0]['customFields']
    except Exception as e:
        logger.error(e)
        return False

    for row in data:
        db_row = {}
        for col,val in row.iteritems():
            if col in db_col_names: db_row[col] = smart_text(val)
        try:
            field, created = CustomField.objects.update_or_create(id=row['id'], defaults=db_row)
        except Exception as e:
            logger.error(e)
            return False
    return True


def process_wrike_contacts():
    """
    Fetches contacts(users) from Wrike's Mercy Corps account and stores them.
    """
    try:
        access_token = get_wrike_access_token()
        headers = {"Authorization": "bearer %s" % access_token}
        contacts = requests.get(settings.WRIKE_CONTACT_API_URL, headers=headers)
        contacts_json = json.loads(contacts.text)
    except Exception as e:
        logger.error(e)
        return False

    db_col_names = get_model_fields_names('Contact')

    try:
        data = contacts_json['data']
    except Exception as e:
        logger.error(e)
        return False

    for row in data:
        db_row = {}
        for col,val in row.iteritems():
            if col in db_col_names: db_row[col] = smart_text(val)
        try:
            contact, created = Contact.objects.update_or_create(id=row['id'], defaults=db_row)
        except Exception as e:
            logger.error(e)
            return False
    return True


def process_wrike_folders():
    """
    Fetches Folder(Projects) from Wrike's Mercy Corps account and stores them.
    """
    try:
        access_token = get_wrike_access_token()
        headers = {"Authorization": "bearer %s" % access_token}
        folders = requests.get(settings.WRIKE_FOLDER_API_URL, headers=headers)
        folders_json = json.loads(folders.text)
    except Exception as e:
        logger.error(e)
        return False

    db_col_names = get_model_fields_names('Folder')

    try:
        data = folders_json['data']
    except Exception as e:
        logger.error(e)
        return False

    for row in data:
        db_row = {}
        for col,val in row.iteritems():
            if col == "project":
                db_row["status"] = smart_text(val['status'])
                timestamp = datetime.datetime.strptime(val['createdDate'][:19], "%Y-%m-%dT%H:%M:%S")
                timestamp = timestamp.replace(tzinfo=pytz.UTC)
                db_row["createdDate"] = timestamp
            if col in db_col_names: db_row[col] = smart_text(val)
        try:
            folder, created = Folder.objects.update_or_create(id=row['id'], defaults=db_row)
        except Exception as e:
            logger.error(e)
            return False
    return True




def process_wrike_tasks():
    """
    Fetch tasks from wrike's api.
    """
    access_token = get_wrike_access_token()
    headers = {"Authorization": "bearer %s" % access_token}
    tasks = requests.get(settings.WRIKE_TASK_API_URL, headers=headers)
    tasks_json = tasks.json()
    nextPageToken = tasks_json.get('nextPageToken', None)
    process_wrike_tasks_helper(tasks_json.get('data', None))
    try:
        while True:
            # Wrike limits # of returned tasks to 1000. So I need to pagingate
            tasks = requests.get("%s&%s=%s" % (settings.WRIKE_TASK_API_URL, "nextPageToken", nextPageToken), headers=headers)
            tasks_json = tasks.json()
            data = tasks_json.get('data', None)
            process_wrike_tasks_helper(data)
            nextPageToken = tasks_json.get('nextPageToken', None)
            if nextPageToken == None:
                break
    except Exception as e:
        logger.error(e)
        return False
    return True

def process_wrike_tasks_helper(data):
    """
    A helper method for processing wrike's tasks and saving them into database
    """
    db_col_names = get_model_fields_names('Task')

    for row in data:
        db_row = {}
        customfields = None
        parentIds = None
        responsibleIds = None

        for col, val in row.iteritems():
            if col == "customFields":
                customfields = val
            elif col == "parentIds":
                parentIds = val
            elif col == "responsibleIds":
                responsibleIds = val
            elif col == "createdDate" or col == "updatedDate" or col == "completedDate":
                try:
                    timestamp = datetime.datetime.strptime(val[:19], "%Y-%m-%dT%H:%M:%S")
                    timestamp = timestamp.replace(tzinfo=pytz.UTC)
                    db_row[col] = timestamp
                except Exception as e:
                    logger.error(e)
                    continue
            elif col == "briefDescription" or col == "title":
                db_row[col] = smart_text("%s..." % val[:250])
            else:
                if col in db_col_names: db_row[col] = smart_text(val)

        task, created = Task.objects.update_or_create(id=row['id'], defaults=db_row)

        # Associate task with custom_fields and its values
        for field in customfields:
            try:
                customfield = CustomField.objects.get(pk=field['id'])
                qcft, created = CustomFieldTask.objects.update_or_create(task=task, customfield=customfield, defaults={'value': smart_text(field['value'])})
            except Exception as e:
                logger.error(e)
                continue

        # Associate task with folders (parents)
        for pid in parentIds:
            try:
                folder = Folder.objects.get(pk=pid)
                task.folders.add(folder)
            except Exception as e:
                logger.error(e)
                continue

        # Associate task with contacts, i.e. those who are responsible for it.
        for rid in responsibleIds:
            try:
                assignee = Contact.objects.get(pk=rid)
                task.assignees.add(assignee)
            except Exception as e:
                logger.error(e)
                continue
    return True




