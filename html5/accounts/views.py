from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import UserSerializer
from html5dicom.models import UserChangePassword, Role, Institution


class UserCreate(APIView):
    """
    Creates the user.
    """

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                UserChangePassword.objects.create(user=user, changepassword=True)
                institution = Institution.objects.get(short_name=request.data['institution'])
                Role.objects.create(name='pac', user=user, institution=institution, max_rows=1000)
                return Response({'status': 'created'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'description': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
