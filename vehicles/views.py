from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Vehicle
from .forms import VehicleForm

@login_required(login_url="/auth/login/")
def dashboard(request):
    if request.user.is_authenticated:
        return render(request, "dashboard/main.html")
    else:
        messages.error(request, "You need to be logged in to access this page.")
        return redirect("login")


class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = "vehicles/vehicle_list.html"
    context_object_name = "vehicles"

    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user)


class VehicleDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Vehicle
    template_name = "vehicles/vehicle_detail.html"

    def test_func(self):
        vehicle = self.get_object()
        return vehicle.owner == self.request.user


class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/vehicle_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class VehicleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/vehicle_form.html"

    def test_func(self):
        vehicle = self.get_object()
        return vehicle.owner == self.request.user


class VehicleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Vehicle
    template_name = "vehicles/vehicle_confirm_delete.html"
    success_url = reverse_lazy("vehicle-list")

    def test_func(self):
        vehicle = self.get_object()
        return vehicle.owner == self.request.user
