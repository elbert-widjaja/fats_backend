from django.test import TestCase, Client
from django.shortcuts import reverse
from rest_framework import status
from api import models
from api.tests.utils.mock import mockStudent, mockAdmin


class AuthTest(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.student = models.Student.objects.create_user(
            user_id=mockStudent['matric'],
            username=mockStudent['username'],
            password=mockStudent['password'],
        )
        cls.admin = models.Admin.objects.create_user(
            username=mockAdmin['username'],
            password=mockAdmin['password'],
        )

    def test_user_should_be_able_to_login_with_correct_domain(self):
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': mockStudent['username'],
            'password': mockStudent['password'],
            'domain': 'student'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_user_should_not_be_able_to_login_with_incorrect_domain(self):
        response1 = self.client.post(reverse('token_obtain_pair'), {
            'username': mockStudent['username'],
            'password': mockStudent['password'],
            'domain': 'admin',  # wrong domain
        })
        response2 = self.client.post(reverse('token_obtain_pair'), {
            'username': mockAdmin['username'],
            'password': mockAdmin['password'],
            'domain': 'student',  # wrong domain
        })

        self.assertEqual(response1.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(response1.data['detail'], "No user found for this domain")
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertRegex(response2.data['detail'], "No user found for this domain")

    def test_user_should_not_be_able_to_login_with_invalid_credentials(self):
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'foo',
            'password': 'bar',
            'domain': 'student'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


