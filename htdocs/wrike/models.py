from __future__ import unicode_literals

from django.contrib.auth.models import User

from django.db import models

# Create your models here.
class CustomField(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=254, null=True, blank=True)
    ctype = models.CharField(max_length=30, null=True, blank=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return title


class Contact(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    fname = models.CharField(max_length=100, null=True, blank=True)
    lname = models.CharField(max_length=100, null=True, blank=True)
    ctype = models.CharField(max_length=30, null=True, blank=True)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)



class Folder(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=254, null=True, blank=True)
    scope = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return title


class Task(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=254, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    brief_description = models.CharField(max_length=254, null=True, blank=True)
    responsible_ids = models.ManyToManyField(Contact, related_name="tasks")
    folders = models.ManyToManyField(Folder, related_name="tasks")
    customfields = models.ManyToManyField(
        CustomField,
        through = 'CustomFieldTask',
        through_fields = ('task', 'customfield')
    )
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return title


class CustomFieldTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    customfield = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    value = models.CharField(max_length=254, null=True, blank=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return "%s=%s" % (customfield, value)


class WrikeOauth2Credentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    access_token = models.CharField(max_length=100, null=False, blank=False)
    token_type = models.CharField(max_length=20, null=False, blank=False)
    refresh_token = models.CharField(max_length=100, null=False, blank=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_time_access_token_fetched = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return access_token

