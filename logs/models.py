from django.db import models
from django.utils.translation import gettext_lazy as _
from vehicles.models import Vehicle


class ServiceType(models.TextChoices):
    OIL_CHANGE = "oil", _("Oil Change")
    TYRE = "tyre", _("Tyre Replacement")
    BRAKE = "brake", _("Brake Service")
    INSPECTION = "insp", _("Inspection")
    OTHER = "other", _("Other")


class MaintenanceLog(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="maintenance_logs"
    )
    date = models.DateField(help_text="Date of service.")
    mileage = models.PositiveIntegerField(help_text="Odometer reading at service.")
    service_type = models.CharField(
        max_length=16,
        choices=ServiceType.choices,
        default=ServiceType.OTHER,
        help_text="Type of maintenance performed.",
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Maintenance Log"
        verbose_name_plural = "Maintenance Logs"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["vehicle", "date"]),
        ]

    def __str__(self):
        return f"{self.get_service_type_display()} on {self.date} ({self.vehicle.reg_number})"


class ExpenseCategory(models.TextChoices):
    FUEL = "fuel", _("Fuel")
    REPAIR = "repair", _("Repair")
    INSURANCE = "ins", _("Insurance")
    TAX = "tax", _("Tax")
    OTHER = "other", _("Other")


class Expense(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="expenses"
    )
    date = models.DateField(help_text="Date expense occurred.")
    category = models.CharField(
        max_length=16,
        choices=ExpenseCategory.choices,
        default=ExpenseCategory.OTHER,
        help_text="Expense category.",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Amount in GBP (£)."
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["vehicle", "category"]),
        ]

    def __str__(self):
        return f"£{self.amount} {self.get_category_display()} on {self.date}"
