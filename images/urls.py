from django.urls import path
from .views import (
    ImageUploadView,
    UserImagesListView,
    generate_expiring_link,
    GenerateExpiringLinkView,
    serve_expiring_image,
)

urlpatterns = [
    path("upload/", ImageUploadView.as_view(), name="upload"),
    path("", UserImagesListView.as_view(), name="list_images"),
    path("images", UserImagesListView.as_view(), name="list_images"),
    path("generate-link/", GenerateExpiringLinkView.as_view(), name="generate-link"),
    path(
        "expiring/<uuid:link_uuid>/", serve_expiring_image, name="serve_expiring_image"
    ),
]
