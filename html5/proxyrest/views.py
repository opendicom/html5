from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
import uuid
from proxyrest.models import SessionRest, StaticParameter, Institution


@api_view(['GET'])
def rest_login(request, *args, **kwargs):
    if 'institution' in kwargs and 'user' in kwargs and 'password' in kwargs:
        try:
            institution = Institution.objects.get(name=kwargs.get('institution'))
        except Institution.DoesNotExist:
            return Response({'error': 'institution does not exist'}, status=status.HTTP_401_UNAUTHORIZED)
        user = authenticate(username=kwargs.get('user'), password=kwargs.get('password'))
        if user:
            try:
                parameter = StaticParameter.objects.get(user=user, active=True, institution=institution)
            except StaticParameter.DoesNotExist:
                return Response({'error': 'not allowed to work with institution {0}'.format(kwargs.get('institution'))},
                                status=status.HTTP_401_UNAUTHORIZED)
            uid = create_session_rest(user, parameter)
            return Response({'session': uid}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'missing params'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def rest_logout(request, *args, **kwargs):
    if 'session' in kwargs:
        try:
            sessionrest = SessionRest.objects.get(sessionid=kwargs.get('session'))
            sessionrest.delete()
            return Response({'logout': 'ok'}, status=status.HTTP_200_OK)
        except SessionRest.DoesNotExist:
            return Response({'error': 'session not exist'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'missing parameter'}, status=status.HTTP_400_BAD_REQUEST)


def create_session_rest(user, StaticParameter):
    uid = uuid.uuid4()
    sessionrest = SessionRest(sessionid=uid.hex,
                              start_date=timezone.now(),
                              expiration_date=timezone.now() + timezone.timedelta(minutes=5),
                              parameter=StaticParameter)
    sessionrest.save()
    return uid.hex


def validate_session_expired(sessionrest):
    if sessionrest.expiration_date >= timezone.now():
        sessionrest.expiration_date = timezone.now() + timezone.timedelta(minutes=5)
        sessionrest.save()
        return True
    else:
        sessionrest.delete()
        return False


@api_view(['GET'])
def qido(request, *args, **kwargs):
    if 'session' in kwargs:
        try:
            sessionrest = SessionRest.objects.get(sessionid=kwargs.get('session'))
        except SessionRest.DoesNotExist:
            return Response({'error': 'invalid credentials, session not exist'}, status=status.HTTP_401_UNAUTHORIZED)
        if validate_session_expired(sessionrest):
            full_path = request.get_full_path()
            current_path = full_path[full_path.index('qido/') + 5:]
            current_path = sessionrest.parameter.institution.url + current_path + sessionrest.parameter.parameter
            qido_response = requests.get(current_path)
            if qido_response.text != '':
                data_response = qido_response.json()
                for item in data_response:
                    if '00081190' in item:
                        study_data = item['00081190']['Value'][0]
                        study_data = study_data[study_data.index('rs') + 3:]
                        wado_url = request.scheme + '://' + request.get_host() + '/proxydcmweb/session/'
                        wado_url = wado_url + kwargs.get('session') + '/wado/' + study_data
                        item['00081190']['Value'] = [wado_url]
                return Response(data_response, status=status.HTTP_200_OK)
            else:
                return Response({}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'session expired'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'missing parameter'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def wado(request, *args, **kwargs):
    if 'session' in kwargs:
        try:
            sessionrest = SessionRest.objects.get(sessionid=kwargs.get('session'))
        except SessionRest.DoesNotExist:
            return Response({'error': 'invalid credentials, session not exist'}, status=status.HTTP_401_UNAUTHORIZED)
        if validate_session_expired(sessionrest):
            full_path = request.get_full_path()
            current_path = full_path[full_path.index('wado/') + 5:]
            current_path = sessionrest.parameter.institution.url + current_path
            headers = {'Accept': 'multipart/related; type=application/dicom;'}
            wado_response = requests.get(current_path, headers=headers)
            return HttpResponse(wado_response.content, status=wado_response.status_code,
                                content_type=wado_response.headers.get('content-type'))
        else:
            return Response({'error': 'session expired'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'missing parameter'}, status=status.HTTP_400_BAD_REQUEST)
