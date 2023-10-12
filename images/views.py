from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponseNotFound
from .models import Image, ExpiringLink
from .serializers import ImageSerializer, ExpiringLinkSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import generics, permissions


# Create your views here.


class ImageUploadView(generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)


# rest_framework list (links only)


class UserImagesListView(generics.ListAPIView):
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Image.objects.filter(profile=self.request.user.profile)


@permission_classes([permissions.IsAuthenticated])
def generate_expiring_link(image, expiration_seconds):
    user_profile = image.profile
    if not user_profile.account_tier.expiring_link_access:
        raise ValueError("Requested function isn't allowed in your current plan.")
    if expiration_seconds < 300 or expiration_seconds > 30000:
        raise ValueError("Expiration time must be set between 300 and 30000 seconds")
    if not expiring_link_exists(image):
        expiring_link = ExpiringLink(image=image)
    else:
        expiring_link = ExpiringLink.objects.filter(image=image).first()
    expiring_link.generate_link(seconds=expiration_seconds)
    expiring_link.save()
    return expiring_link.get_full_url()


def expiring_link_exists(image):
    return ExpiringLink.objects.filter(image=image).exists()


class GenerateExpiringLinkView(APIView):
    serializer_class = ExpiringLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data["image"]
            if image.profile.user == request.user:
                try:
                    link = generate_expiring_link(
                        image,
                        serializer.validated_data["expiration_time"],
                    )
                    return Response({"link": link})
                except ValueError as e:
                    return Response({"error": str(e)}, status=400)
        return Response(serializer.errors, status=400)


def serve_expiring_image(request, link_uuid):
    link = get_object_or_404(ExpiringLink, link=link_uuid)

    # check if link expired
    if link.expiration_time < timezone.now():
        # error 404 if link has expired
        return HttpResponseNotFound("The link has expired :(")
    return redirect(link.image.image.url)
