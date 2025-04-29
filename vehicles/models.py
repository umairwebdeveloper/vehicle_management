import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Vehicle(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vehicles",
        verbose_name="Owner",
        help_text="User who added this vehicle.",
    )
    reg_number = models.CharField(
        "Registration Number",
        max_length=12,
        unique=True,
        db_index=True,
        help_text="UK-style plate, e.g. AB12CDE.",
    )
    make = models.CharField(
        "Make", max_length=64, help_text="Manufacturer, e.g. Ford, Toyota."
    )
    model = models.CharField(
        "Model", max_length=64, help_text="Model name or number, e.g. Fiesta."
    )
    year = models.PositiveIntegerField(
        "Year of Manufacture", help_text="Four-digit year, e.g. 2018."
    )
    vin = models.CharField(
        "Vehicle VIN",
        max_length=17,
        blank=True,
        null=True,
        help_text="17-character Vehicle Identification Number.",
    )
    photo = models.ImageField(
        "Photo",
        upload_to="vehicles/photos/%Y/%m/",
        blank=True,
        help_text="Optional vehicle image.",
    )
    share_uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique token for sharing this vehicle via a link.",
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        ordering = ["-added_at"]
        indexes = [
            models.Index(fields=["owner", "reg_number"]),
        ]

    def __str__(self):
        return f"{self.reg_number} — {self.make} {self.model} ({self.year})"

    def get_absolute_url(self):
        return reverse("vehicle-detail", kwargs={"pk": self.pk})

    def get_share_url(self):
        return reverse("vehicle-share", kwargs={"share_uuid": str(self.share_uuid)})
