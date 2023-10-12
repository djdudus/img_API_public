from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.test import TestCase
from images.models import Image, Profile, AccountTier


class ImageModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.account_tier = AccountTier.objects.create(name="TestTier")
        self.profile = Profile.objects.create(
            user=self.user, account_tier=self.account_tier
        )
        self.image_file = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        )

    def test_image_creation(self):
        # Arrange
        image = Image(profile=self.profile, image=self.image_file)
        # Act
        image.save()
        # Assert
        self.assertTrue("uploaded_images/test_image" in image.image.name)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(image.profile, self.profile)
        self.assertTrue("uploaded_images/test_image" in image.image.name)
        self.assertTrue(image.image.name.startswith("uploaded_images/test_image"))
