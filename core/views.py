from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
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

            return redirect("food_listings")

    else:
        form = FoodListingForm()

    return render(
        request,
        "core/create_food_listing.html",
        {"form": form},
    )


def get_own_listing(request, pk):
    """Return the listing only if it belongs to the logged-in user.

    Anyone else (another Donor or a Recipient) gets a 404, so they
    cannot edit or delete it and cannot tell whether it exists.
    """
    return get_object_or_404(FoodListing, pk=pk, donor=request.user)


@login_required
def my_food_listings(request):
    # Only Donors have their own listings to manage.
    if request.user.role != User.Role.DONOR:
        raise PermissionDenied(
            "Only Donors can manage food listings."
        )

    listings = FoodListing.objects.filter(
        donor=request.user
    ).order_by("collection_deadline")

    return render(
        request,
        "core/my_food_listings.html",
        {"listings": listings},
    )


@login_required
def edit_food_listing(request, pk):
    listing = get_own_listing(request, pk)
    original_title = listing.title

    if request.method == "POST":
        form = FoodListingForm(request.POST, instance=listing)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f'"{listing.title}" was updated.'
            )

            return redirect("my_food_listings")

    else:
        form = FoodListingForm(instance=listing)

    return render(
        request,
        "core/edit_food_listing.html",
        {"form": form, "listing_title": original_title},
    )


@login_required
def delete_food_listing(request, pk):
    listing = get_own_listing(request, pk)

    # A GET request only shows the confirmation page.
    # The listing is deleted only after the Donor confirms (POST).
    if request.method == "POST":
        title = listing.title
        listing.delete()

        messages.success(
            request,
            f'"{title}" was deleted.'
        )

        return redirect("my_food_listings")

    return render(
        request,
        "core/delete_food_listing.html",
        {"listing": listing},
    )
