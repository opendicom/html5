from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from proxyrest.models import TokenAccessPatient, TokenAccessStudy, SessionRest


class TokenAccessPatientSerializer(serializers.ModelSerializer):
    viewer_choice = ['cornerstone', 'weasis', 'zip', 'osirix']
    token = serializers.CharField(validators=[UniqueValidator(queryset=TokenAccessPatient.objects.all())])
    PatientID = serializers.CharField(write_only=True)
    IssuerOfPatientID = serializers.CharField(required=False, default='', allow_blank=True, write_only=True)
    IssuerOfPatientIDQualifiers = serializers.JSONField(required=False, default='', write_only=True)
    StudyDate = serializers.CharField(required=False, default='', allow_blank=True, write_only=True)
    viewerType = serializers.ChoiceField(choices=viewer_choice, allow_blank=True, write_only=True)
    seriesSelection = serializers.JSONField(required=False, default='', write_only=True)
    start_date = serializers.DateTimeField
    expiration_date = serializers.DateTimeField
    role_id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        token = TokenAccessPatient.objects.create(token=validated_data['token'],
                                                  PatientID=validated_data['PatientID'],
                                                  IssuerOfPatientID=validated_data['IssuerOfPatientID'],
                                                  IssuerOfPatientIDQualifiers=validated_data['IssuerOfPatientIDQualifiers'],
                                                  StudyDate=validated_data['StudyDate'],
                                                  viewerType=validated_data['viewerType'],
                                                  seriesSelection=validated_data['seriesSelection'],
                                                  start_date=validated_data['start_date'],
                                                  expiration_date=validated_data['expiration_date'],
                                                  role_id=validated_data['role_id'])
        return token

    class Meta:
        model = TokenAccessPatient
        fields = ('token', 'PatientID', 'IssuerOfPatientID', 'IssuerOfPatientIDQualifiers', 'StudyDate',
                  'viewerType', 'seriesSelection', 'start_date', 'expiration_date', 'role_id')


class TokenAccessStudySerializer(serializers.ModelSerializer):
    access_choice = ['osirix.zip', 'weasis.xml', 'dicom.zip', 'cornerstone.json', 'datatablesseries.json', 'datatablespatient.json']
    token = serializers.CharField(validators=[UniqueValidator(queryset=TokenAccessStudy.objects.all())])
    accessType = serializers.ChoiceField(choices=access_choice, write_only=True)
    StudyInstanceUID = serializers.CharField(allow_blank=True, write_only=True)
    SeriesInstanceUID = serializers.CharField(allow_blank=True, write_only=True)
    AccessionNumber = serializers.CharField(allow_blank=True, write_only=True)
    StudyDate = serializers.CharField(allow_blank=True, write_only=True)
    PatientID = serializers.CharField(allow_blank=True, write_only=True)
    issuer = serializers.CharField(allow_blank=True, write_only=True)
    SeriesDescription = serializers.CharField(allow_blank=True, write_only=True)
    Modality = serializers.CharField(allow_blank=True, write_only=True)
    SOPClass = serializers.CharField(allow_blank=True, write_only=True)
    SeriesNumber = serializers.CharField(allow_blank=True, write_only=True)
    SOPClassOff = serializers.CharField(allow_blank=True, write_only=True)
    transferSyntax = serializers.CharField(allow_blank=True, write_only=True)
    start_date = serializers.DateTimeField
    expiration_date = serializers.DateTimeField
    role_id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        token = TokenAccessStudy.objects.create(token=validated_data['token'],
                                                accessType=validated_data['accessType'],
                                                StudyInstanceUID=validated_data['StudyInstanceUID'],
                                                SeriesInstanceUID=validated_data['SeriesInstanceUID'],
                                                AccessionNumber=validated_data['AccessionNumber'],
                                                StudyDate=validated_data['StudyDate'],
                                                PatientID=validated_data['PatientID'],
                                                issuer=validated_data['issuer'],
                                                SeriesDescription=validated_data['SeriesDescription'],
                                                Modality=validated_data['Modality'],
                                                SOPClass=validated_data['SOPClass'],
                                                SeriesNumber=validated_data['SeriesNumber'],
                                                SOPClassOff=validated_data['SOPClassOff'],
                                                transferSyntax=validated_data['transferSyntax'],
                                                start_date=validated_data['start_date'],
                                                expiration_date=validated_data['expiration_date'],
                                                role_id=validated_data['role_id'])
        return token

    class Meta:
        model = TokenAccessStudy
        fields = ('token', 'accessType', 'StudyInstanceUID', 'SeriesInstanceUID', 'AccessionNumber', 'StudyDate',
                  'PatientID', 'issuer', 'SeriesDescription', 'Modality', 'SOPClass', 'SeriesNumber', 'SOPClassOff',
                  'transferSyntax', 'start_date', 'expiration_date', 'role_id')


class SessionRestSerializer(serializers.ModelSerializer):
    sessionid = serializers.CharField(validators=[UniqueValidator(queryset=SessionRest.objects.all())])
    start_date = serializers.DateTimeField
    expiration_date = serializers.DateTimeField()
    role_id = serializers.IntegerField()

    def create(self, validated_data):
        sessionrest = SessionRest.objects.create(sessionid=validated_data['sessionid'],
                                                 start_date=validated_data['start_date'],
                                                 expiration_date=validated_data['expiration_date'],
                                                 role_id=validated_data['role_id'])
        return sessionrest

    class Meta:
        model = SessionRest
        fields = ('sessionid', 'start_date', 'expiration_date', 'role_id')
