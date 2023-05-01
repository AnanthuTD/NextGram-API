from django.forms import model_to_dict
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import json

User = get_user_model()


class Post(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse('post')
        print('url: %s' % self.url)
        self.user = User.objects.create(
            username='testuser2', password='testPassword#')

    def test_post_view(self):
        user_dict = model_to_dict(self.user)
        newuser = {'username': user_dict['username'],
                   'first_name': user_dict['first_name'],
                   'last_name': user_dict['last_name'],
                   'email': user_dict['email'],
                  }
        print(newuser)
        post_data = {
            'user': newuser,
            'like': ['user1', 'user2'],
            'shares': ['user3'],
            'description': 'Test post description',
            'hash_tag': ['tag1', 'tag2'],
            'mentions': ['user4'],
            'location': 'Test location',
            'post': SimpleUploadedFile('media/default-profiel-pic.svg', b'content')
        }
        with open('media/default-profiel-pic.svg', 'rb') as f:
            post_data['post'] = SimpleUploadedFile(
                'media/default-profiel-pic.svg', b'content')

        response = self.client.post(self.url, post_data)

        print('response : ', response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'status': True})
