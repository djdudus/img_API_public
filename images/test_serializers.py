from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from images.models import Image, Profile, AccountTier
from images.serializers import ImageSerializer


class ImageSerializerTestCase(TestCase):
    def setUp(self):
        # Creating a user
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        # Assuming you have an AccountTier model, creating a "Basic" account tier
        self.account_tier = AccountTier.objects.create(name="Basic")

        # Creating a profile for the user with the "Basic" account tier
        self.profile = Profile.objects.create(
            user=self.user, account_tier=self.account_tier
        )

        # Creating an image associated with the user's profile
        self.image_file = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        self.image = Image.objects.create(profile=self.profile, image=self.image_file)

        # Setting up the serializer context with the request
        self.serializer_context = {"request": RequestFactory().get("/")}
        self.serializer_context["request"].user = self.user

    def test_image_serializer_basic_tier(self):
        """Testing the ImageSerializer with a Basic account tier"""

        serializer = ImageSerializer(
            instance=self.image, context=self.serializer_context
        )
        data = serializer.data

        # Checking that "image" key is not present for Basic account tier
        self.assertNotIn("image", data)
