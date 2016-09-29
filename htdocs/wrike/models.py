from __future__ import unicode_literals

import datetime, time

from django.db import models

from django.utils import timezone
from django.utils.timezone import utc

from django.contrib.auth.models import User


class BaseManager(models.Manager):
    """
    extends the default django manager to include a method that returns
    none if the given model doesn't exists.
    """
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class BaseModel(models.Model):
    """
    Abstract class that overrides the default django manager to include a new method called get_or_none
    """
    created = models.DateTimeField(editable=False, auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, blank=True, null=True)
    objects = BaseManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        now_utc = datetime.datetime.utcnow().replace(tzinfo=utc)
        if self.created:
            self.updated = now_utc
        super(BaseModel, self).save(*args, **kwargs)



class CustomField(BaseModel):
    id = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=254, null=True, blank=True)
    type = models.CharField(max_length=30, null=True, blank=True)
    deleted = models.BooleanField(default=False)


    def __unicode__(self):
        return title

    def __str__(self):
        return title


class Contact(BaseModel):
    id = models.CharField(max_length=100, primary_key=True)
    firstName = models.CharField(max_length=100, null=True, blank=True)
    lastName = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=30, null=True, blank=True)
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s %s" % (self.firstName, self.lastName)

    def __str__(self):
        return "%s %s" % (self.firstName, self.lastName)


class Folder(BaseModel):
    id = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=254, null=True, blank=True)
    scope = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title



class Task(BaseModel):
    id = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=254, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    briefDescription = models.CharField(max_length=254, null=True, blank=True)
    importance = models.CharField(max_length=100, null=True, blank=True)
    permalink = models.URLField(max_length=200, null=True, blank=True)
    scope = models.CharField(max_length=40, null=True, blank=True)
    createdDate = models.DateTimeField(blank=True, null=True)
    updatedDate = models.DateTimeField(blank=True, null=True)
    completedDate = models.DateTimeField(blank=True, null=True)
    assignees = models.ManyToManyField(Contact, related_name="tasks")
    folders = models.ManyToManyField(Folder, related_name="tasks")
    customfields = models.ManyToManyField(
        CustomField,
        through = 'CustomFieldTask',
        through_fields = ('task', 'customfield')
    )

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title


class CustomFieldTask(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    customfield = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    value = models.CharField(max_length=254, null=True, blank=True)

    def __unicode__(self):
        return "%s=%s" % (self.customfield, self.value)

    def __str__(self):
        return "%s=%s" % (self.customfield, self.value)



class WrikeOauth2Credentials(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    access_token = models.CharField(max_length=100, null=False, blank=False)
    token_type = models.CharField(max_length=20, null=False, blank=False)
    refresh_token = models.CharField(max_length=100, null=False, blank=False)
    last_time_access_token_fetched = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.access_token

    def __str__(self):
        return self.access_token


