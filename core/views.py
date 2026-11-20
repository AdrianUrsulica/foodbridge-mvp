from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

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