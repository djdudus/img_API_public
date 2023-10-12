from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...models import AccountTier, ThumbnailSize, Profile


class Command(BaseCommand):
    help = "Initialize the default data"

    def handle(self, *args, **kwargs):  # sourcery skip: extract-duplicate-method
        # Create Thumbnail Sizes
        size_200 = ThumbnailSize.objects.get_or_create(height=200)[0]
        size_400 = ThumbnailSize.objects.get_or_create(height=400)[0]

        # Create Account Tiers
        basic_tier = AccountTier.objects.get_or_create(name="Basic")[0]
        basic_tier.thumbnail_sizes.add(size_200)

        premium_tier = AccountTier.objects.get_or_create(name="Premium")[0]
        premium_tier.thumbnail_sizes.add(size_200, size_400)
        premium_tier.original_link_access = True
        premium_tier.save()

        enterprise_tier = AccountTier.objects.get_or_create(name="Enterprise")[0]
        enterprise_tier.thumbnail_sizes.add(size_200, size_400)
        enterprise_tier.original_link_access = True
        enterprise_tier.expiring_link_access = True
        enterprise_tier.save()

        # Create Users
        basic_user = User.objects.create_user("basic", password="basic")
        Profile.objects.get_or_create(user=basic_user, account_tier=basic_tier)

        premium_user = User.objects.create_user("premium", password="premium")
        Profile.objects.get_or_create(user=premium_user, account_tier=premium_tier)

        enterprise_user = User.objects.create_user("enterprise", password="enterprise")
        Profile.objects.get_or_create(
            user=enterprise_user, account_tier=enterprise_tier
        )

        # Create superuser
        admin_user = User.objects.create_superuser(
            "admin", email=None, password="admin"
        )
        Profile.objects.get_or_create(user=admin_user, account_tier=enterprise_tier)

        self.stdout.write(self.style.SUCCESS("Data initialized successfully"))
