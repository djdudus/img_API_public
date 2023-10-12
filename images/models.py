from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import timedelta
import uuid


# Create your models here.


class AccountTier(models.Model):
    name = models.CharField(max_length=30, unique=True)
    thumbnail_sizes = models.ManyToManyField("ThumbnailSize")
    original_link_access = models.BooleanField(default=False)
    expiring_link_access = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class ThumbnailSize(models.Model):
    height = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.height)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_tier = models.ForeignKey(AccountTier, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class Image(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploaded_images/")
    uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name


class Thumbnail(models.Model):
    image = models.ForeignKey(
        Image, related_name="thumbnails", on_delete=models.CASCADE
    )
    thumbnail = models.ImageField(upload_to="thumbnails/")
    size = models.ForeignKey(ThumbnailSize, on_delete=models.CASCADE)


class ExpiringLink(models.Model):
    link = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
    )
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    expiration_time = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expiration_time

    # link generation with it's default time set to 1 hour
    def generate_link(self, seconds=3600):
        self.expiration_time = timezone.now() + timedelta(seconds=seconds)

    def get_full_url(self):
        relative_url = reverse("serve_expiring_image", args=[str(self.link)])
        site_url = "127.0.0.1"
        return f"http://{site_url}{relative_url}"
