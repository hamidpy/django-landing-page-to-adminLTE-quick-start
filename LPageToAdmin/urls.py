from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views  # Only keep if you have global views in this file

urlpatterns = [
    # Core views
    path('admin/', admin.site.urls),  # Django admin interface
    path('', views.HOME, name='home'),  # Home page
    path('', include('app.urls')),  # Ensure app-specific URLs are included

    # Include app-specific routes
    path('useradmin/', include('app.urls')),  # Include app-specific admin routes
    path('signup/', views.signup, name='signup'),  # Signup page
    path('accounts/', include('django.contrib.auth.urls')),  # Django auth views
    path('orders/', views.orders_view, name='orders'),  # Orders route
    path('reports/', views.reports_view, name='reports'),  # Route for Reports page
    path('request-quote/', views.request_quote_view, name='request_quote'),  # Quote request
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
