from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "reg_number",
        "owner",
        "make",
        "model",
        "year",
        "added_at",
    )
    list_filter = (
        "make",
        "year",
    )
    search_fields = (
        "reg_number",
        "owner__username",
        "make",
        "model",
    )
    readonly_fields = (
        "added_at",
        "updated_at",
        "share_uuid",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "owner",
                    "reg_number",
                    "make",
                    "model",
                    "year",
                    "vin",
                    "photo",
                )
            },
        ),
        (
            "Sharing",
            {
                "classes": ("collapse",),
                "fields": ("share_uuid",),
                "description": "Unique UUID for public sharing.",
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("added_at", "updated_at"),
            },
        ),
    )
