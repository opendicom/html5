from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Organization(BaseModel):
    name = models.CharField(max_length=64, blank=False, null=False)
    short_name = models.CharField(max_length=64, blank=False, null=False)
    oid = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.short_name

    class Meta:
        unique_together = ('short_name', 'oid')


class Institution(BaseModel):
    name = models.CharField(max_length=64, blank=False, null=False)
    short_name = models.CharField(max_length=64, blank=False, null=False)
    oid = models.CharField(max_length=64, blank=True, null=True)
    logo_data = models.BinaryField(blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, blank=False, null=False)

    def __str__(self):
        return '%s - %s' % (self.organization.short_name, self.short_name)

    class Meta:
        unique_together = ('short_name', 'oid', 'organization')


class Service(BaseModel):
    name = models.CharField(max_length=64, blank=False, null=False)
    oid = models.CharField(max_length=64, blank=True, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.DO_NOTHING, blank=False, null=False)

    def __str__(self):
        return '%s - %s - %s' % (self.institution.organization.short_name, self.institution.short_name, self.name)

    class Meta:
        unique_together = ('name', 'oid', 'institution')


class Role(BaseModel):
    role_choices = (
        ('rad', 'Radiologo'),
        ('sol', 'Solicitante'),
        ('aut', 'Autenticador'),
        ('med', 'Medico'),
        ('res', 'Rest'),
        ('pac', 'Paciente'),
    )
    name = models.CharField(max_length=3, choices=role_choices)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    institution = models.ForeignKey(Institution, on_delete=models.DO_NOTHING, blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING, blank=True, null=True)
    default = models.BooleanField(default=False)
    max_rows = models.IntegerField(default=100, blank=False, null=False)
    parameter_rest = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return '(%s) - (%s) - (%s) - (%s)' % (self.name, self.user, self.institution, self.service)

    class Meta:
        unique_together = (('name', 'user', 'service'), ('name', 'user', 'institution'))


class RoleType(models.Model):
    id = models.BigAutoField(max_length=3, primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=3, blank=False, null=False)


class Alternate(BaseModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)


class Setting(BaseModel):
    key = models.CharField(max_length=50, blank=False, null=False)
    value = models.CharField(max_length=255, blank=False, null=False)


class UserChangePassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, primary_key=True)
    changepassword = models.BooleanField(default=False, blank=False, null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)


class UserViewerSettings(BaseModel):
    viewer_choices = (
        ('htm', 'Ver estudio'),
        ('dow', 'Descargar'),
        ('osi', 'Osirix'),
        ('wea', 'Weasis'),
    )
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, unique=True)
    viewer = models.CharField(max_length=3, choices=viewer_choices, blank=True, null=True)
