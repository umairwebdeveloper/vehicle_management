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
from datetime import datetime

# from .snippets import fetch_vehicle_from_mot


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = "/auth/login/"
    template_name = "dashboard/main.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        # Read raw date params
        start_str = self.request.GET.get("start_date")
        end_str = self.request.GET.get("end_date")

        # Parse dates if provided
        start_date = None
        end_date = None
        try:
            if start_str:
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        except ValueError:
            start_date = None
        try:
            if end_str:
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        except ValueError:
            end_date = None

        vehicle_filters = {"owner": user}
        expense_filters = {"vehicle__owner": user}
        maintenance_filters = {"vehicle__owner": user}
        post_filters = {"author": user}

        if start_date:
            vehicle_filters["added_at__date__gte"] = start_date
            expense_filters["date__gte"] = start_date
            maintenance_filters["date__gte"] = start_date
            post_filters["created__date__gte"] = start_date
        if end_date:
            vehicle_filters["added_at__date__lte"] = start_date
            expense_filters["date__lte"] = end_date
            maintenance_filters["date__lte"] = end_date
            post_filters["created__date__lte"] = end_date

        # All user vehicles, expenses & maintenance
        vehicles = Vehicle.objects.filter(**vehicle_filters)
        expenses = Expense.objects.filter(**expense_filters)
        maintenance = MaintenanceLog.objects.filter(**maintenance_filters)
        posts = Post.objects.filter(**post_filters)

        # Key metrics
        context = super().get_context_data(**kwargs)
        context["start_date"] = start_str
        context["end_date"] = end_str

        context["vehicles_count"] = vehicles.count()
        context["expense_count"] = expenses.count()
        context["maintenance_count"] = maintenance.count()

        # Number of distinct expense categories used
        expense_cat_qs = expenses.values("category").distinct()
        context["category_count"] = expense_cat_qs.count()

        # … inside get_context_data(), after you define `vehicles` …
        vehicle_time_qs = (
            vehicles
            .annotate(month=TruncMonth('added_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        context['vehicles_months'] = [
            item['month'].strftime('%b %Y') for item in vehicle_time_qs
        ]
        context['vehicles_month_counts'] = [
            item['count'] for item in vehicle_time_qs
        ]

        # Total spent
        context["total_spent_expenses"] = (
            expenses.aggregate(total=Sum("amount"))["total"] or 0
        )
        context["total_spent_maintenance"] = (
            maintenance.aggregate(total=Sum("amount"))["total"] or 0
        )
        context["total_spent"] = (
            context["total_spent_expenses"] + context["total_spent_maintenance"]
        )

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
