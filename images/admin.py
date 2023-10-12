from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import AccountTier, ThumbnailSize, Profile, Image, ExpiringLink


# Register your models here.
admin.site.register(AccountTier)
admin.site.register(ThumbnailSize)
admin.site.register(Profile)
admin.site.register(Image)
admin.site.register(ExpiringLink)


# edited form to include account tier for user when created
class CustomUserCreationForm(UserCreationForm):
    account_tier = forms.ModelChoiceField(queryset=AccountTier.objects.all())

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "account_tier")


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "account_tier"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if (
            not change
        ):  # meaning the object is being created, so create a profile for the user
            account_tier = form.cleaned_data["account_tier"]
            Profile.objects.create(user=obj, account_tier=account_tier)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
