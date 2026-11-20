from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils import timezone

from accounts.models import User
from .forms import FoodListingForm
from .models import FoodListing


@login_required
def food_listings(request):
    listings = FoodListing.objects.filter(
        status=FoodListing.Status.AVAILABLE,
        collection_deadline__gt=timezone.now(),
    ).order_by("collection_deadline")

    return render(
        request,
        "core/food_listings.html",
        {"listings": listings},
    )


@login_required
def create_food_listing(request):
    # Only authenticated Donors can create listings.
    if request.user.role != User.Role.DONOR:
        raise PermissionDenied(
            "Only Donors can create food listings."
        )

    if request.method == "POST":
        form = FoodListingForm(request.POST)

        if form.is_valid():
            # Create listing without saving yet.
            listing = form.save(commit=False)

            # Automatically assign the logged-in Donor.
            listing.donor = request.user

            # Save the listing to the database.
            listing.save()

            messages.success(
                request,
                "Food listing created successfully!"
            )

            # Temporary redirect until FB-10 integration.
            return redirect("donor_home")

    else:
        form = FoodListingForm()

    return render(
        request,
        "core/create_food_listing.html",
        {"form": form},
    )
