from django.urls import path
from .views import ExpenseCreateView, ExpenseUpdateView, ExpenseDeleteView

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
]
