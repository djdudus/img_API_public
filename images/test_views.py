from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from PIL import Image as PILImage
from io import BytesIO
from datetime import timedelta
from django.utils import timezone
from images.models import Image, Profile, AccountTier, ExpiringLink
from images.views import generate_expiring_link

expiration_date = timezone.now() + timedelta(hours=24)


class ImageUploadViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.account_tier = AccountTier.objects.create(name="TestTier")
        self.profile = Profile.objects.create(
            user=self.user, account_tier=self.account_tier
        )

    def test_image_upload_view(self):
        # Arrange
        self.client.force_login(self.user)
        url = reverse("upload")
        image_stream = BytesIO()
        image = PILImage.new("RGB", (100, 100))
        image.save(image_stream, format="JPEG")
        image_stream.seek(0)

        image_file = SimpleUploadedFile(
            "test_image.jpg", image_stream.getvalue(), content_type="image/jpeg"
        )

        data = {
            "profile": self.profile.id,
            "image": image_file,
        }
        # Act
        response = self.client.post(url, data=data)
        # Assert
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Image.objects.first().profile, self.profile)
        self.assertTrue(
            Image.objects.first().image.name.startswith("uploaded_images/test_image")
        )


class GenerateExpiringLinkTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.account_tier = AccountTier.objects.create(
            name="TestTier", expiring_link_access=True
        )
        self.profile = Profile.objects.create(
            user=self.user, account_tier=self.account_tier
        )
        user_profile = self.user.profile
        user_profile.account_tier.expiring_link_access = True
        user_profile.save()
        self.image = Image.objects.create(profile=self.profile, image="test_image.jpg")

        self.expiring_link = ExpiringLink.objects.create(
            image=self.image, expiration_time=expiration_date
        )

    def test_generate_expiring_link_valid_input(self):
        link = generate_expiring_link(self.image, 3600)
        self.assertIsNotNone(link)
        self.assertEqual(link, self.expiring_link.get_full_url())

    def test_generate_expiring_link_invalid_account_tier(self):
        self.user.profile.account_tier.expiring_link_access = False
        self.user.profile.account_tier.save()
        with self.assertRaisesMessage(
            ValueError, "Requested function isn't allowed in your current plan."
        ):
            generate_expiring_link(self.image, 3600)

    def test_generate_expiring_link_invalid_expiration_time(self):
        with self.assertRaisesMessage(
            ValueError, "Expiration time must be set between 300 and 30000 seconds"
        ):
            generate_expiring_link(self.image, 200)

    def test_generate_expiring_link_existing_link(self):
        link = generate_expiring_link(self.image, 3600)
        self.assertIsNotNone(link)
        self.assertEqual(link, self.expiring_link.get_full_url())

    def test_generate_expiring_link_no_link_exists(self):
        self.expiring_link.delete()
        link = generate_expiring_link(self.image, 3600)
        self.assertIsNotNone(link)
        self.assertEqual(
            link, ExpiringLink.objects.get(image=self.image).get_full_url()
        )


class GenerateExpiringLinkViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client = APIClient()
        self.client.force_login(self.user)
        self.account_tier = AccountTier.objects.create(
            name="TestTier", expiring_link_access=True
        )
        self.profile = Profile.objects.create(
            user=self.user, account_tier=self.account_tier
        )
        self.image = Image.objects.create(profile=self.profile, image="test_image.jpg")

    def test_generate_expiring_link_success(self):
        url = reverse("generate-link")
        data = {
            "image": self.image.id,
            "expiration_time": 3600,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("link", response.data)

    def test_generate_expiring_link_invalid_image(self):
        url = reverse("generate-link")
        data = {
            "image": 9999,  # Invalid image ID
            "expiration_time": 3600,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("image", response.data)
        self.assertIn("Invalid pk", str(response.data["image"]))

    def test_generate_expiring_link_unauthorized_user(self):
        url = reverse("generate-link")
        data = {
            "image": self.image.id,
            "expiration_time": 3600,
        }
        unauthorized_client = APIClient()
        response = unauthorized_client.post(url, data=data)
        self.assertEqual(response.status_code, 403)
