from django.db import models
from html5dicom.models import Role


class SessionRest(models.Model):
    sessionid = models.CharField(max_length=32, primary_key=True)
    start_date = models.DateTimeField()
    expiration_date = models.DateTimeField()
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)
