from django.forms import ModelForm
from html5dicom.models import UserViewerSettings


class UserViewerSettingsForm(ModelForm):
    class Meta:
        model = UserViewerSettings
        fields = ['viewer']
