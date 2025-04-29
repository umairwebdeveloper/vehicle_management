from django.urls import path
from . import views


urlpatterns = [
    path("", views.VehicleListView.as_view(), name="vehicle-list"),
    path("add/", views.VehicleCreateView.as_view(), name="vehicle-add"),
    path("<int:pk>/", views.VehicleDetailView.as_view(), name="vehicle-detail"),
    path("<int:pk>/edit/", views.VehicleUpdateView.as_view(), name="vehicle-edit"),
    path("<int:pk>/delete/", views.VehicleDeleteView.as_view(), name="vehicle-delete"),
]
