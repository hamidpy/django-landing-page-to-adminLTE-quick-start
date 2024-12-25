from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views
from app import views as app_views  # Import app-level views
from .views import USERADMIN
from .views import revenue_view
from LPageToAdmin.views import pending_orders_view  # Import your pending orders view
from LPageToAdmin.views import order_delete  # Import the order_delete function
from LPageToAdmin.views import admin_leads_view
from .views import admin_submit_lead
from app.views import submit_lead  # Import the frontend view
from . import views
from .views import reports_view, reports_export


from .views import (
    pending_orders_view,
    orders_view,
    view_order,
    edit_order,
    order_delete,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('base/', views.BASE, name='base'),  # Base page
    path('adminpage/base/', views.ADMINBASE, name='adminbase'),  # Admin base
    path('', views.HOME, name='home'),  # Landing page
    path('useradmin/', views.USERADMIN, name='useradmin'),  # Admin dashboard
    path('signup', views.signup, name='signup'),  # Signup page
    path('accounts/', include('django.contrib.auth.urls')),  # Authentication
    path('admin/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='admin_login'),
    path("", include("app.urls")),  # Include app-level URLs
    path('reports/', views.reports_view, name='reports'),
    path("reports/export/", reports_export, name="reports_export"),  # New export route
    path("admin/revenue/", revenue_view, name="revenue"),
    path('view_message/<int:id>/', views.view_message, name='view_message'),
    path("adminleads/", views.admin_submit_lead, name="adminleads"),  # Admin leads view
    path("adminleads/delete/<int:lead_id>/", views.delete_lead, name="delete_lead"),
    path('adminmessages/delete/<int:message_id>/', views.delete_message, name='delete_message'),
    path("admininbox/", views.admin_inbox, name="admininbox"),
    path("adminleads/", views.admin_leads_view, name="adminleads"),
    # Admin Quotes Management
    path("adminquotes/", views.admin_quotes_view, name="adminquotes"),  # Main admin quotes view
    path("adminquotes/<int:quote_id>/", views.admin_quotes_view, name="adminquote_detail"),  # For a specific quote
    path("adminquotes/delete/<int:quote_id>/", views.delete_quote, name="delete_quote"),  # Delete a quote
    # Main orders management routes
    path('admin/orders/', orders_view, name='orders'),  # All orders
    path('admin/orders/pending/', pending_orders_view, name='pending_orders'),  # Pending orders
    path('admin/orders/<int:id>/', view_order, name='view_order'),  # View specific order
    path('admin/orders/edit/<int:id>/', edit_order, name='edit_order'),  # Edit specific order
    path('admin/orders/delete/<int:order_id>/', order_delete, name='order_delete'),  # Delete order
    path("", include("app.urls")),   # Include app's urls.py for the landing page
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
