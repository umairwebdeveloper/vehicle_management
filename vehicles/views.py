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
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from logs.models import Expense, MaintenanceLog, ExpenseCategory
from django.views.generic import TemplateView
from forum.models import Post, CAT_CHOICES
# from .snippets import fetch_vehicle_from_mot


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login/"
    template_name = "dashboard/main.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        # All user vehicles, expenses & maintenance
        vehicles = Vehicle.objects.filter(owner=user)
        expenses = Expense.objects.filter(vehicle__owner=user)
        maintenance = MaintenanceLog.objects.filter(vehicle__owner=user)

        # Key metrics
        context = super().get_context_data(**kwargs)
        context["vehicles_count"] = vehicles.count()
        context["expense_count"] = expenses.count()
        context["maintenance_count"] = maintenance.count()

        # Number of distinct expense categories used
        expense_cat_qs = expenses.values("category").distinct()
        context["category_count"] = expense_cat_qs.count()

        # Total spent
        context["total_spent"] = expenses.aggregate(total=Sum("amount"))["total"] or 0

        # Expense by category
        cat_totals_qs = expenses.values("category").annotate(total=Sum("amount"))
        context["category_labels"] = [
            dict(ExpenseCategory.choices)[item["category"]] for item in cat_totals_qs
        ]
        context["category_totals"] = [float(item["total"]) for item in cat_totals_qs]

        # Maintenance frequency by month
        maint_qs = (
            maintenance.annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        context["maint_months"] = [item["month"].strftime("%b %Y") for item in maint_qs]
        context["maint_counts"] = [item["count"] for item in maint_qs]

        # Expenses distribution per vehicle
        veh_exp_qs = expenses.values("vehicle__reg_number").annotate(
            total=Sum("amount")
        )
        context["vehicle_labels"] = [item["vehicle__reg_number"] for item in veh_exp_qs]
        context["vehicle_totals"] = [float(item["total"]) for item in veh_exp_qs]

        posts = Post.objects.filter(author=user)
        # Basic counts
        context["posts_count"] = posts.count()
        context["solved_posts_count"] = posts.filter(solved=True).count()
        context["unsolved_posts_count"] = posts.filter(solved=False).count()

        # Distribution by category
        post_cat_qs = posts.values("cat").annotate(count=Count("id"))
        context["posts_cat_labels"] = [
            dict(CAT_CHOICES)[item["cat"]] for item in post_cat_qs
        ]
        context["posts_cat_counts"] = [item["count"] for item in post_cat_qs]

        # Posts over time (monthly)
        post_time_qs = (
            posts.annotate(month=TruncMonth("created"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        context["posts_months"] = [
            itm["month"].strftime("%b %Y") for itm in post_time_qs
        ]
        context["posts_month_counts"] = [itm["count"] for itm in post_time_qs]

        return context


class VehicleListView(LoginRequiredMixin, ListView):
    login_url = "/auth/login/"
    model = Vehicle
    template_name = "vehicles/vehicle_list.html"
    context_object_name = "vehicles"

    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user)


class VehicleDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    login_url = "/auth/login/"
    model = Vehicle
    template_name = "vehicles/vehicle_detail.html"

    def test_func(self):
        vehicle = self.get_object()
        return vehicle.owner == self.request.user


class VehicleCreateView(LoginRequiredMixin, CreateView):
    login_url = "/auth/login/"
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/vehicle_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Vehicle added successfully.")
        return response


class VehicleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    login_url = "/auth/login/"
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/vehicle_form.html"

    def test_func(self):
        vehicle = self.get_object()
        return vehicle.owner == self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Vehicle updated successfully.")
        return response


class VehicleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    login_url = "/auth/login/"
    model = Vehicle
    template_name = "vehicles/vehicle_confirm_delete.html"
    success_url = reverse_lazy("vehicle-list")

    def test_func(self):
        vehicle = self.get_object()
        return vehicle.owner == self.request.user

    def delete(self, request, *args, **kwargs):
        vehicle = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Vehicle {vehicle.reg_number} deleted.")
        return response
