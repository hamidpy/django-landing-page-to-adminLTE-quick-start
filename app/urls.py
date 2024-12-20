from django.urls import path
from . import views
from app.models import Quote
from .views import home
from app.views import submit_lead
from .views import request_quote
from django.views.generic import TemplateView

# Define routes and map to their respective view functions
urlpatterns = [
    # Existing routes
    path("inbox/", views.inbox_view, name="inbox"),  # Add the inbox route
    path("submit-lead/", submit_lead, name="submit_lead"),
    path("projects/", views.projects_view, name="projects"),  # Admin manage projects
    path("reports/", views.reports_view, name="reports"),  # Route for Reports page
    # app/urls.py
    path("quote-success/", views.quote_success, name="quote-success"),  # Success page
    path("", home, name="home"),  # Route for the landing page
    path("request-quote/", request_quote, name="request_quote"),
    path("", TemplateView.as_view(template_name="pages/index.html"), name="landing_page"),
]
