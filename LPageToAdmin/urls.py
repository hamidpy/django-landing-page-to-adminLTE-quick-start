from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views
from app import views as app_views  # Import app-level views
from .views import USERADMIN
from .views import pending_orders_view
from .views import revenue_view


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
    path('admin/leads/', app_views.admin_leads_view, name='leads'),
    path('quotes/', views.quotes_view, name='quotes'),
    path('reports/', views.reports_view, name='reports'),
    path("admin/pending-orders/", pending_orders_view, name="pending_orders"),
    path("admin/revenue/", revenue_view, name="revenue"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
