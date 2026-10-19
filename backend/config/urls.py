from django.urls import path

from planner.views import config_view, plan_view

urlpatterns = [
    path("api/config/", config_view, name="config"),
    path("api/plan/", plan_view, name="plan"),
]
