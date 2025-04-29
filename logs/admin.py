from django.contrib import admin
from .models import MaintenanceLog, Expense


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle",
        "date",
        "mileage",
        "service_type",
        "created_at",
    )
    list_filter = (
        "service_type",
        "date",
        "vehicle__make",
    )
    search_fields = (
        "vehicle__reg_number",
        "notes",
    )
    date_hierarchy = "date"
    raw_id_fields = ("vehicle",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle",
        "date",
        "category",
        "amount",
        "created_at",
    )
    list_filter = (
        "category",
        "date",
    )
    search_fields = (
        "vehicle__reg_number",
        "notes",
    )
    date_hierarchy = "date"
    raw_id_fields = ("vehicle",)
