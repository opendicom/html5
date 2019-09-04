from django.db import models
from html5dicom.models import Role


class SessionRest(models.Model):
    sessionid = models.CharField(max_length=32, primary_key=True)
    start_date = models.DateTimeField()
    expiration_date = models.DateTimeField()
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)


class TokenAccessPatient(models.Model):
    token = models.CharField(max_length=32, primary_key=True)
    PatientID = models.CharField(max_length=20)
    IssuerOfPatientID = models.CharField(max_length=64, blank=True, null=True)
    IssuerOfPatientIDQualifiers = models.TextField(blank=True, null=True)
    StudyDate = models.CharField(max_length=17, blank=True, null=True)
    viewerType = models.CharField(max_length=11, blank=True, null=True)
    seriesSelection = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    expiration_date = models.DateTimeField()
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ('token', 'PatientID'),


class TokenAccessStudy(models.Model):
    token = models.CharField(max_length=32, primary_key=True)
    viewerType = models.CharField(max_length=11)
    StudyInstanceUID = models.CharField(max_length=255, blank=True, null=True)
    AccessionNumber = models.CharField(max_length=255, blank=True, null=True)
    StudyDate = models.CharField(max_length=20, blank=True, null=True)
    PatientID = models.CharField(max_length=20, blank=True, null=True)
    issuer = models.CharField(max_length=255, blank=True, null=True)
    SeriesDescription = models.TextField(blank=True, null=True)
    Modality = models.CharField(max_length=20, blank=True, null=True)
    SOPClass = models.TextField(blank=True, null=True)
    SeriesNumber = models.CharField(max_length=20, blank=True, null=True)
    start_date = models.DateTimeField()
    expiration_date = models.DateTimeField()
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ('token', 'StudyInstanceUID'),
