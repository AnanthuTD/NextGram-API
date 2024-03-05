from django.core.management.base import BaseCommand
from django.forms import model_to_dict
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from PIL import Image
from io import BytesIO
from django.contrib.auth import authenticate

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.client = Client()
        self.url = reverse('post')

        # Fetch existing users
        self.users = User.objects.filter(is_superuser=False)
        self.test_post_creation_for_all_users()

    def generate_fake_image(self):
        """Generate a fake image and return its content"""
        width = 640
        height = 480
        # Generate a random color string using faker
        color = fake.hex_color()
        image = Image.new("RGB", (width, height), color)
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        return image_io.getvalue()

    def test_post_creation_for_all_users(self):
        for user in self.users:
            # Authenticate the user
            authenticated_user = authenticate(self.client.request, phone_email_username=user.get_username(), password=user.get_username())
            if authenticated_user is not None:
                self.client.force_login(authenticated_user)
                print("Logged in as:", user.username)
            else: 
                print('==========================Error===============================')
                print('Login failed')
                print('==============================================================')
                exit()
            
            # Generate fake image
            fake_image_content = self.generate_fake_image()
            
            # Prepare post data with fake information
            post_data = {
                'user': model_to_dict(user, fields=['username', 'first_name', 'last_name', 'email', 'id']),
                # 'like': ['user1', 'user2'],
                # 'shares': ['user3'],
                'description': fake.sentence(),
                'hash_tag': [fake.word() for _ in range(2)],
                # 'mentions': ['user4'],
                'location': fake.city(),
                'file': SimpleUploadedFile('fake_image.jpg', fake_image_content)
            }
            
            print(post_data)

            # Send POST request to create a post
            response = self.client.post(self.url, post_data, format='multipart')

            self.stdout.write(self.style.SUCCESS('Successfully generated fake posts with images.'))


