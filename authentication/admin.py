from django.contrib import admin
from .models import Profile
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "image",
        "bio",
        "location",
        "website",
        "birthday",
        "phone_number",
        "country",
        "city",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__username", "user__email")
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)