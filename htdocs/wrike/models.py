from __future__ import unicode_literals

from django.contrib.auth.models import User

from django.db import models


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
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    objects = BaseManager()

    class Meta:
        abstract = True



# Create your models here.
class CustomField(BaseModel):
    id = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=254, null=True, blank=True)
    ctype = models.CharField(max_length=30, null=True, blank=True)


    def __unicode__(self):
        return title


class Contact(BaseModel):
    id = models.CharField(max_length=100, primary_key=True)
    fname = models.CharField(max_length=100, null=True, blank=True)
    lname = models.CharField(max_length=100, null=True, blank=True)
    ctype = models.CharField(max_length=30, null=True, blank=True)
    deleted = models.BooleanField(default=False)



class Folder(BaseModel):
    id = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=254, null=True, blank=True)
    scope = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return title


class Task(BaseModel):
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

    def __unicode__(self):
        return title


class CustomFieldTask(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    customfield = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    value = models.CharField(max_length=254, null=True, blank=True)

    def __unicode__(self):
        return "%s=%s" % (customfield, value)


class WrikeOauth2Credentials(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    access_token = models.CharField(max_length=100, null=False, blank=False)
    token_type = models.CharField(max_length=20, null=False, blank=False)
    refresh_token = models.CharField(max_length=100, null=False, blank=False)
    last_time_access_token_fetched = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return access_token

