from rest_framework import serializers
from .models import Image, Profile, Thumbnail, ThumbnailSize, ExpiringLink
from PIL import Image as PILImage
from io import BytesIO
from django.core.files import File
from django.core.files.storage import default_storage


class ImageSerializer(serializers.ModelSerializer):
    thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ("id", "image", "thumbnails")

    def get_thumbnails(self, obj):
        # get thumbnail sizes for current tier
        account_tier = self.context["request"].user.profile.account_tier
        thumbnail_heights = account_tier.thumbnail_sizes.all()

        return {
            f"{height.height}px": self.create_thumbnail(obj, height.height)
            for height in thumbnail_heights
        }

    # show only values allowed for tier
    def to_representation(self, instance):
        value = super().to_representation(instance)
        account_tier_name = self.context["request"].user.profile.account_tier.name
        if account_tier_name == "Basic":
            value.pop("image", None)
        return value

    def create_thumbnail(self, obj, height):
        thumbnail = self._get_thumbnail(obj, height) or self._generate_thumbnail(
            obj, height
        )

        request = self.context.get("request")
        return request.build_absolute_uri(thumbnail.thumbnail.url)

    def _get_thumbnail(self, obj, height):
        # Try to fetch an existing thumbnail.

        return Thumbnail.objects.filter(image=obj, size__height=height).first()

    def _generate_thumbnail(self, obj, height):
        # Generate and save a new thumbnail using PIL.

        image = obj.image
        p_image = PILImage.open(image)
        thumbnail_io = self._create_resized_image(p_image, height, image.name)

        thumbnail_size = ThumbnailSize.objects.get(height=height)
        thumbnail = Thumbnail(
            image=obj,
            thumbnail=File(thumbnail_io, name=f"thumbnail_{height}px_{image.name}"),
            size=thumbnail_size,
        )
        thumbnail.save()
        return thumbnail

    def _create_resized_image(self, p_image, height, image_name):
        # Resize the image using the specified height and return it as BytesIO.

        ratio = p_image.width / p_image.height
        new_width = int(ratio * height)
        p_image.thumbnail((new_width, height))

        # Determine image format
        img_format = "JPEG" if image_name.lower().endswith(".jpg") else "PNG"

        # Store thumbnail using BytesIO for higher performance
        thumbnail_io = BytesIO()
        p_image.save(thumbnail_io, format=img_format)
        return thumbnail_io


class ExpiringLinkSerializer(serializers.Serializer):
    image = serializers.PrimaryKeyRelatedField(queryset=Image.objects.all())
    expiration_time = serializers.IntegerField(min_value=300, max_value=30000)

    def __init__(self, *args, **kwargs):
        super(ExpiringLinkSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            self.fields["image"].queryset = Image.objects.filter(
                profile=request.user.profile
            )
