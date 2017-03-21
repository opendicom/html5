from django.db import models
from django.contrib.auth.models import User


class Institution(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=64, blank=False, null=False)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class StaticParameter(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    institution = models.ForeignKey(Institution, on_delete=models.DO_NOTHING)
    parameter = models.CharField(max_length=255, blank=False, null=False)
    active = models.BooleanField(default=False)


class SessionRest(models.Model):
    sessionid = models.CharField(max_length=32, primary_key=True)
    start_date = models.DateTimeField()
    expiration_date = models.DateTimeField()
    parameter = models.ForeignKey(StaticParameter, on_delete=models.DO_NOTHING)
