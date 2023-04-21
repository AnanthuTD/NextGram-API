from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
import json

class SignupViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('signup')
        self.valid_payload = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'phone_or_email': 'testuser@example.com',
            'id_user': 1,
            'bio': 'Test user',
            'location': 'Test location'
        }
        self.invalid_payload = {
            'username': 'testuser',
            'email': 'invalidemail',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'phone_or_email': 'invalidphone',
            'id_user': 1,
            'bio': 'Test user',
            'location': 'Test location'
        }

    def test_valid_signup(self):
        response = self.client.post(self.url, json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        print ("response : " , response.json())
        self.assertEqual(response.json()['success'], True)
        """ self.assertIsNotNone(response.json()['errors']['username'])
        self.assertEqual(response.json()['errors']['email'], self.valid_payload['email'])
        self.assertEqual(response.json()['errors']['phone'], self.valid_payload['phone_or_email'])
        self.assertEqual(response.json()['errors']['id_user'], self.valid_payload['id_user'])
        self.assertEqual(response.json()['errors']['bio'], self.valid_payload['bio'])
        self.assertEqual(response.json()['errors']['location'], self.valid_payload['location']) """

    def test_invalid_signup(self):
        response = self.client.post(self.url, json.dumps(self.invalid_payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertTrue('email' in response.json()['errors'])
        self.assertTrue('phone_or_email' in response.json()['errors'])
