from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect
from app.models import Lead, Message, Order, Project, Quote, UserCreateForm



# Base Views
def BASE(request):
    return render(request, "base/base.html")


def ADMINBASE(request):
    return render(request, "base/adminbase.html")


# Home View
def HOME(request):
    """Renders the homepage."""
    context = {"static_example": "/static/assets/img/testimonial-1.jpg"}
    return render(request, "pages/index.html", context)


# User Registration (Signup)
def signup(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
            login(request, new_user)
            return redirect("login")
    else:
        form = UserCreateForm()

    context = {"form": form}
    return render(request, "registration/signup.html", context)


# Email Utility
def send_quote_email(to_email, subject, message):
    """Send a quote email using Django's send_mail function."""
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=False,
    )

@csrf_protect
@login_required
def USERADMIN(request):
    try:
        # Key Metrics
        new_leads_count = Lead.objects.filter(status="new").count()
        pending_orders_count = Order.objects.filter(status="pending").count()
        completed_projects_count = Project.objects.filter(status="completed").count()
        monthly_revenue = (
            Order.objects.filter(date__month=now().month).aggregate(Sum("amount")).get("amount__sum", 0) or 0
        )
        total_quotes = Quote.objects.count()
        orders_in_progress = Order.objects.filter(status="in-progress").count()
        sales_completed = Order.objects.filter(status="completed").count()

        # Calculate Conversion Rate
        total_leads = Lead.objects.count()
        conversion_rate = (
            (sales_completed / total_leads) * 100 if total_leads > 0 else 0
        )

        # Popular Window Styles
        popular_window_styles = (
            Project.objects.values("window_style")
            .annotate(style_count=Count("window_style"))
            .order_by("-style_count")[:5]
        )

        # Sales Chart Data (Revenue by Month)
        sales_data = (
            Order.objects.annotate(month=ExtractMonth("date"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )
        sales_chart_labels = [f"Month {data['month']}" for data in sales_data]
        sales_chart_data = [data["total"] for data in sales_data]

        # Recent Leads
        recent_leads = Lead.objects.order_by("-created_at")[:5]

        # Debugging Outputs
        print("Context:", context)
        
    except Exception as e:
        # Log error and set default values
        print(f"Error fetching data: {e}")
        new_leads_count = 29
        pending_orders_count = 6
        completed_projects_count = 2
        monthly_revenue = 43300.33
        total_quotes = 0
        orders_in_progress = 0
        sales_completed = 0
        conversion_rate = 20.5
        popular_window_styles = []
        sales_chart_labels = ["January", "February", "March"]
        sales_chart_data = [5000,7000,8000]
        recent_leads = []

    # Context for the template
    context = {
        "metrics": {
            "new_leads_count": new_leads_count,
            "pending_orders_count": pending_orders_count,
            "completed_projects_count": completed_projects_count,
            "monthly_revenue": monthly_revenue,
            "total_quotes": total_quotes,
            "orders_in_progress": orders_in_progress,
            "sales_completed": sales_completed,
            "conversion_rate": round(conversion_rate, 2),
        },
        "popular_window_styles": popular_window_styles,
        "sales_chart_labels": sales_chart_labels,
        "sales_chart_data": sales_chart_data,
        "leads": recent_leads,
    }

    # Render the admin dashboard template with context
    return render(request, "adminPages/adminhome.html", context)

# Sidebar Views

def leads_view(request):
    leads = Lead.objects.all()  # Query all leads
    paginator = Paginator(leads, 50)  # Show 50 leads per page
    page_number = request.GET.get(
        "page"
    )  # Get the page number from the query parameters
    page_obj = paginator.get_page(page_number)  # Fetch the corresponding page
    return render(request, "adminPages/adminleads.html", {"page_obj": page_obj})


def revenue_view(request):
    """
    Handles the revenue details view.
    """
    # Example data for demonstration
    revenue_data = [43300.33]  # Replace with your actual query or calculations
    return render(request, "adminPages/revenue.html", {"revenue_data": revenue_data})

def pending_orders_view(request):
    # Example data for demonstration
    pending_orders = [6]  # Replace with your actual data query
    return render(request, "adminPages/pending_orders.html", {"pending_orders": pending_orders})


def orders_view(request):
    orders = Order.objects.all()
    return render(request, "adminPages/adminorders.html", {"orders": orders})


def quotes_view(request):
    quotes = Quote.objects.all()
    return render(request, "adminPages/adminquotes.html", {"quotes": quotes})


def projects_view(request):
    projects = Project.objects.all()
    return render(request, "adminPages/adminprojects.html", {"projects": projects})


def reports_view(request):
    """Handles generating reports."""
    return render(request, "adminPages/adminreports.html")


# Inbox View
def inbox_view(request):
    messages = Message.objects.all().order_by("-created_at")
    return render(request, "adminPages/admininbox.html", {"messages": messages})


# Logout View
def logout_view(request):
    """Logs the user out and redirects to the home page."""
    logout(request)
    return redirect("home")


# Quote Request View
def request_quote_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        name = request.POST.get("name")
        phone = request.POST.get("phone")

        subject = "Thank you for requesting a quote!"
        message = f"Hi {name},\n\nThank you for reaching out! We'll contact you soon at {phone}."
        send_quote_email(email, subject, message)

        return redirect("quote-success")
    return render(request, "request_quote.html")


@csrf_protect
def quick_lead_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            Lead.objects.create(email=email, name="Anonymous")
            messages.success(request, "Your email has been submitted successfully!")
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
    return render(request, "user_landing.html")  # Ensure this template exists
    path(
        "userlanding/", views.user_landing, name="user_landing"
    ),  # Define the URL pattern


def user_landing(request):
    """
    Handle requests to the user landing page.
    """
    if request.method == "GET":
        # Load the landing page
        return render(request, "pages/user_landing.html")

    elif request.method == "POST":
        # Handle form submissions if you have a form
        email = request.POST.get("email", "")
        if email:  # Check if email is valid
            # Add a success message
            messages.success(request, "Thank you! Your email has been submitted.")
        else:
            # Add an error message if no email is provided
            messages.error(request, "Please provide a valid email.")

        # Reload the page with the success/error messages
        return render(request, "pages/user_landing.html")

    # Default fallback for unsupported methods
    return render(request, "pages/user_landing.html")



