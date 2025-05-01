from django.urls import path
from .views import ExpenseCreateView, ExpenseUpdateView, ExpenseDeleteView, MaintenanceLogCreateView, MaintenanceLogUpdateView, MaintenanceLogDeleteView

urlpatterns = [
    path(
        "vehicle/<int:vehicle_pk>/expense/add/",
        ExpenseCreateView.as_view(),
        name="expense-create",
    ),
    path(
        "expense/<int:pk>/edit/",
        ExpenseUpdateView.as_view(),
        name="expense-edit",
    ),
    path(
        "expense/<int:pk>/delete/",
        ExpenseDeleteView.as_view(),
        name="expense-delete",
    ),
    path(
        "vehicles/<int:vehicle_pk>/maintenance/add/",
        MaintenanceLogCreateView.as_view(),
        name="vehicle-maintenance-add",
    ),
    path(
        "maintenance/<int:pk>/edit/",
        MaintenanceLogUpdateView.as_view(),
        name="maintenance-edit",
    ),
    path(
        "maintenance/<int:pk>/delete/",
        MaintenanceLogDeleteView.as_view(),
        name="maintenance-delete",
    ),
]
