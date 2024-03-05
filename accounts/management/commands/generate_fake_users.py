import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile
from PIL import Image
import uuid
from faker import Faker

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Generates fake users, profiles, and posts with images'

    def handle(self, *args, **kwargs):

        # Create fake users and profiles
        for _ in range(20):
            # Generate fake user data
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.email()
            username = fake.user_name()
            password = str(username)
            print('username: ', username, ', password: ', password)

            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password,
                                             first_name=first_name, last_name=last_name)

            # Create profile for the user
            # Generate fake phone number with 10 digits
            phone = fake.phone_number().replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
            phone = phone[:10]  # Trim to 10 digits if longer
            bio = fake.text()
            location = fake.city()
            gender = fake.random_element(elements=('Male', 'Female', 'Other'))
            website = fake.url()

            profile = Profile.objects.create(user=user, phone=phone, bio=bio,
                                             location=location, gender=gender, website=website)

            # Create fake posts for the user
            """ for _ in range(5):  # Adjust the number of posts per user as needed
                caption = fake.text()
                location = fake.city()
                file_path = self.generate_fake_image()

                post = Post.objects.create(user=user, caption=caption, location=location, file=file_path) """

        self.stdout.write(self.style.SUCCESS('Successfully generated fake users, profiles.'))

    def generate_fake_image(self):
        """Generate a fake image and return its path"""
        # Create a temporary directory to store the image
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate a random image with Pillow
        width = 640
        height = 480
        color = (fake.random_int(0, 255), fake.random_int(0, 255), fake.random_int(0, 255))
        image = Image.new("RGB", (width, height), color)
        
        # Save the image to a temporary file
        file_name = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(temp_dir, file_name)
        image.save(file_path, "JPEG")

        return file_path


