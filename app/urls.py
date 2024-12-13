from django.urls import path
from . import views


urlpatterns = [
    # Existing routes
    path('inbox/', views.inbox_view, name='inbox'),  # Add the inbox route
    path('submit-lead/', views.submit_lead, name='submit_lead'),  # Submit lead route
    path("admin/submit-lead/", views.admin_submit_lead_view, name="admin_submit_lead"),
    path("orders/", views.orders_view, name="orders"),  # Orders route
    path("quotes/", views.quotes_view, name="quotes"),
    path('projects/', views.projects_view, name='projects'),  # Admin manage projects
    path('reports/', views.reports_view, name='reports'),  # Route for Reports page
    path("admin/leads/", views.admin_leads_view, name="leads"),  # Admin manage leads
    path("submit-quote/", views.submit_quote, name="submit_quote"),  # Submit Quote Route
    


]
