from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import UserSerializer
from html5dicom.models import UserChangePassword, UserViewerSettings, Role, Institution
from django.contrib.auth.models import User


class UserCreate(APIView):

    def post(self, request, format='json'):
        try:
            user = User.objects.get(username=request.data['username'])
            serializer = UserSerializer(instance=user,  data=request.data)
        except User.DoesNotExist:
            serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                userviewersettings, create_settings = UserViewerSettings.objects.update_or_create(user=user)
                if create_settings:
                    userviewersettings.viewer = 'cornerstone'
                    userviewersettings.save()
                institution = Institution.objects.get(short_name=request.data['institution'])
                role, create_role = Role.objects.update_or_create(name='pac', user=user)
                role.institution = institution
                role.max_rows = 1000
                role.save()
                return Response({'status': 'created'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'description': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
