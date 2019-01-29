from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from html5dicom.models import Organization, Institution


class UserCreateTests(APITestCase):
    def setUp(self):
        # Create organization and institution for test
        org = Organization.objects.create(name='ORG', short_name='ORG')
        Institution.objects.create(short_name='INST', organization=org)
        # end  create

    def test_order(self):
        self.create_user()
        self.active_user()
        self.update_user()

    def create_user(self):
        url = reverse('account-create')
        data = {
            "institution": "INST",
            "username": "123456",
            "password": "123456789",
            "first_name": "USER NAME",
            "last_name": "LAST NAME",
            "is_active": False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, '123456')
        self.assertEqual(User.objects.get().is_active, False)

    def active_user(self):
        url = reverse('account-create')
        data = {
            "institution": "INST",
            "username": "123456",
            "first_name": "USER NAME",
            "last_name": "LAST NAME",
            "is_active": True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, '123456')
        self.assertEqual(User.objects.get().is_active, True)

    def update_user(self):
        url = reverse('account-create')
        data = {
            "institution": "INST",
            "username": "123456",
            "first_name": "USER NAME UPDATE",
            "last_name": "LAST NAME UPDATE",
            "is_active": True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, '123456')
        self.assertEqual(User.objects.get().first_name, "USER NAME UPDATE")
        self.assertEqual(User.objects.get().last_name, "LAST NAME UPDATE")
        self.assertEqual(User.objects.get().is_active, True)
