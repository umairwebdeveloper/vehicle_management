from django.shortcuts import render, redirect
from .forms import LoginForm, SignUpForm
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data.get("password1"))
            new_user.save()
            messages.success(request, "User registered successfully!")
            return redirect("login")
        else:
            for value in form.errors.values():
                messages.error(request, f"{value}")

    if request.user.is_authenticated:
        return redirect("dashboard")

    form = SignUpForm()
    context = {"form": form}
    return render(request, "authentication/signup.html", context)


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            identifier = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            if User.objects.filter(email=identifier).exists():
                username = (
                    User.objects.filter(email=identifier)
                    .values_list("username", flat=True)
                    .get()
                )
                user = auth.authenticate(request, username=username, password=password)
            else:
                user = auth.authenticate(
                    request, username=identifier, password=password
                )

            if user is not None:
                auth.login(request, user)
                return redirect("dashboard")
            else:
                messages.error(
                    request,
                    "Incorrect username/email or password! Verify and try again.",
                )
                return redirect("login")

    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm()
    context = {"form": form}
    return render(request, "authentication/login.html", context)


def logout(request):
    auth.logout(request)
    return redirect("login")


@login_required(login_url="/auth/login/")
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            auth.update_session_auth_hash(request, user)
            messages.success(request, "Your password was succesfully updated!")
            return redirect("dashboard")
        else:
            messages.error(request, "Ops, an error ocurred! Please, try again :)")

    form = PasswordChangeForm(request.user)
    context = {"form": form}
    return render(request, "dashboard/change_password/change_password.html", context)
