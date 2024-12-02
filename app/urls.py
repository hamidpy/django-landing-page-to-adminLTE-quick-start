from django.urls import path
from . import views
from app import views  # Import your views

urlpatterns = [
    path('', views.USERADMIN, name='useradmin'),  # Admin Dashboard
    path('leads/', views.leads_view, name='leads'),
    path('orders/', views.orders_view, name='orders'),
    path('quotes/', views.quotes_view, name='quotes'),
    path('projects/', views.projects_view, name='projects'),
    path('reports/', views.reports_view, name='reports'),
    path('inbox/', views.inbox_view, name='inbox'),  # Existing inbox URL
    path('message/<int:message_id>/', views.view_message, name='view_message'),  # New URL for viewing a message
    path('orders/<int:order_id>/', views.view_order, name='view_order'),
    path('orders/<int:order_id>/edit/', views.edit_order, name='edit_order'),
    path('submit-lead/', views.submit_lead, name='submit_lead'),
    path('logout/', views.logout_view, name='logout'),
]


