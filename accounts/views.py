from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import RegisterForm
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("role_home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("role_home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def role_home(request):
    if request.user.role == User.Role.DONOR:
        return redirect("donor_home")
    if request.user.role == User.Role.RECIPIENT:
        return redirect("recipient_home")
    return redirect("login")


@login_required
def donor_home(request):
    if request.user.role != User.Role.DONOR:
        return redirect("role_home")

    return render(request, "accounts/donor_home.html")


@login_required
def recipient_home(request):
    if request.user.role != User.Role.RECIPIENT:
        return redirect("role_home")

    return render(request, "accounts/recipient_home.html")


