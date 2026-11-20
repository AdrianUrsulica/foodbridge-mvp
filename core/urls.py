
from django.urls import path
from . import views

urlpatterns = [
    path("", views.food_listings, name="food_listings"),
    path("create/", views.create_food_listing, name="create_food_listing"),
]

