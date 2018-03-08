from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from proxyrest.models import TokenAccessPatient, SessionRest


class TokenAccessPatientSerializer(serializers.ModelSerializer):
    token = serializers.CharField(validators=[UniqueValidator(queryset=TokenAccessPatient.objects.all())])
    patientid = serializers.CharField()
    start_date = serializers.DateTimeField
    expiration_date = serializers.DateTimeField
    role_id = serializers.IntegerField()

    def create(self, validated_data):
        token = TokenAccessPatient.objects.create(token=validated_data['token'],
                                                  patientid=validated_data['patientid'],
                                                  start_date=validated_data['start_date'],
                                                  expiration_date=validated_data['expiration_date'],
                                                  role_id=validated_data['role_id'])
        return token

    class Meta:
        model = TokenAccessPatient
        fields = ('token', 'patientid', 'start_date', 'expiration_date', 'role_id')


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
