from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django import forms
from .models import Expense, MaintenanceLog
from .forms import ExpenseForm, MaintenanceLogForm
from vehicles.models import Vehicle


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    login_url = "/auth/login/"
    model = Expense
    form_class = ExpenseForm
    template_name = "logs/expense_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.vehicle = get_object_or_404(
            Vehicle, pk=kwargs["vehicle_pk"], owner=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["vehicle"].queryset = Vehicle.objects.filter(pk=self.vehicle.pk)
        form.fields["vehicle"].initial = self.vehicle
        form.fields["vehicle"].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        messages.success(self.request, "Expense added.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vehicle"] = self.vehicle
        return context

    def get_success_url(self):
        return reverse_lazy("vehicle-detail", kwargs={"pk": self.vehicle.pk})


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "/auth/login/"
    model = Expense
    form_class = ExpenseForm
    template_name = "logs/expense_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.vehicle.owner != request.user:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields["vehicle"].queryset = Vehicle.objects.filter(
            pk=self.object.vehicle.pk
        )
        form.fields["vehicle"].initial = self.object.vehicle
        form.fields["vehicle"].widget = forms.HiddenInput()

        return form

    def form_valid(self, form):
        messages.success(self.request, "Expense updated.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vehicle"] = self.object.vehicle
        return context

    def get_success_url(self):
        return reverse_lazy("vehicle-detail", kwargs={"pk": self.object.vehicle.pk})


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    login_url = "/auth/login/"
    model = Expense
    template_name = "logs/expense_confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.vehicle.owner != request.user:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, f"Deleted expense: {self.object}")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("vehicle-detail", kwargs={"pk": self.object.vehicle.pk})


class MaintenanceLogCreateView(LoginRequiredMixin, CreateView):
    login_url = "/auth/login/"
    model = MaintenanceLog
    form_class = MaintenanceLogForm
    template_name = "logs/maintenance_form.html"

    def dispatch(self, request, *args, **kwargs):
        # ensure the vehicle exists and belongs to this user
        self.vehicle = get_object_or_404(
            Vehicle, pk=kwargs["vehicle_pk"], owner=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # restrict to this single vehicle, hide the field
        form.fields["vehicle"].queryset = Vehicle.objects.filter(pk=self.vehicle.pk)
        form.fields["vehicle"].initial = self.vehicle
        form.fields["vehicle"].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        messages.success(self.request, "Maintenance record added.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vehicle"] = self.vehicle
        return context

    def get_success_url(self):
        return reverse_lazy("vehicle-detail", kwargs={"pk": self.vehicle.pk})


class MaintenanceLogUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "/auth/login/"
    model = MaintenanceLog
    form_class = MaintenanceLogForm
    template_name = "logs/maintenance_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.vehicle.owner != request.user:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["vehicle"].queryset = Vehicle.objects.filter(
            pk=self.object.vehicle.pk
        )
        form.fields["vehicle"].initial = self.object.vehicle
        form.fields["vehicle"].widget = forms.HiddenInput()
        return form

    def form_valid(self, form):
        messages.success(self.request, "Maintenance record updated.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vehicle"] = self.object.vehicle
        return context

    def get_success_url(self):
        return reverse_lazy("vehicle-detail", kwargs={"pk": self.object.vehicle.pk})


class MaintenanceLogDeleteView(LoginRequiredMixin, DeleteView):
    login_url = "/auth/login/"
    model = MaintenanceLog
    template_name = "logs/maintenance_confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.vehicle.owner != request.user:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, f"Deleted maintenance record: {self.object}")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("vehicle-detail", kwargs={"pk": self.object.vehicle.pk})
