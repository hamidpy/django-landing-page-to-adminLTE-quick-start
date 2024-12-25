from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect
from app.models import Lead, Message, Order, Project, Quote, UserCreateForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages  # Import the messages framework
from django.contrib.auth.decorators import login_required
from app.forms import LeadForm  # Ensure LeadForm is correctly imported
from datetime import datetime
from django import forms
import re
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from app.forms import QuoteForm
from app.models import Quote
from django.http import HttpResponse
import csv


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
    """
    Admin Dashboard View - Displays key metrics, recent leads, and other statistics.
    """
    try:
        # Key Metrics
        new_leads_count = Lead.objects.filter(status="new").count()
        pending_orders_count = Order.objects.filter(status="pending").count()
        completed_projects_count = Project.objects.filter(status="completed").count()
        monthly_revenue = (
            Order.objects.filter(date__month=now().month)
            .aggregate(Sum("amount"))
            .get("amount__sum", 0)
            or 0
        )
        total_quotes = Quote.objects.count()
        orders_in_progress = Order.objects.filter(status="in-progress").count()
        sales_completed = Order.objects.filter(status="completed").count()

        # Calculate Conversion Rate
        total_leads = Lead.objects.count()
        conversion_rate = (
            round((sales_completed / total_leads) * 100, 2) if total_leads > 0 else 0
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

        # Inbox Message Count
        message_count = Message.objects.filter(
            is_read=False
        ).count()  # Example: Count unread messages

    except Exception as e:
        # Log error and set default values
        print(f"Error fetching data: {e}")
        new_leads_count = 0
        pending_orders_count = 0
        completed_projects_count = 0
        monthly_revenue = 0.0
        total_quotes = 0
        orders_in_progress = 0
        sales_completed = 0
        conversion_rate = 0
        popular_window_styles = []
        sales_chart_labels = []
        sales_chart_data = []
        recent_leads = []
        message_count = 0

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
            "conversion_rate": conversion_rate,
            "message_count": message_count,  # Added inbox message count
        },
        "popular_window_styles": popular_window_styles,
        "sales_chart_labels": sales_chart_labels,
        "sales_chart_data": sales_chart_data,
        "leads": recent_leads,
    }

    # Render the admin dashboard template with context
    return render(request, "adminPages/adminhome.html", context)


# Sidebar Views
@staff_member_required
def admin_leads_view(request):
    if request.method == "POST":
        # Handle the form submission
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        service = request.POST.get("service")

        # Save the new lead
        Lead.objects.create(name=name, email=email, phone=phone, service=service)
        messages.success(request, "Lead successfully submitted!")

        # Redirect to the same page after form submission
        return redirect("adminPages/adminleads")

    # Fetch all leads to display
    leads = Lead.objects.all()
    return render(request, "adminPages/adminleads.html", {"leads": leads})


def revenue_view(request):
    """
    Handles the revenue details view.
    """
    # Example data for demonstration
    revenue_data = [43300.33]  # Replace with your actual query or calculations
    return render(request, "adminPages/revenue.html", {"revenue_data": revenue_data})


def pending_orders_view(request):
    """
    View for displaying pending orders and metrics in the adminorders.html template.
    """
    if not request.user.is_staff:  # Ensure only staff/admin users can access
        return redirect("admin:login")

    # Query the database for pending orders
    pending_orders = Order.objects.filter(
        status="pending"
    )  # Adjust status value as needed
    pending_orders_count = pending_orders.count()  # Count pending orders

    # Pass data to the shared adminorders.html template
    return render(
        request,
        "adminPages/adminorders.html",
        {
            "orders": pending_orders,  # Use orders for compatibility with existing template
            "pending_orders_count": pending_orders_count,
            "view_mode": "pending",  # Used to differentiate views in the template
        },
    )


@csrf_protect
def orders_view(request):
    """
    View for managing all orders, including pending orders, dynamically.
    """
    if not request.user.is_staff:  # Restrict access to staff/admin users
        return redirect('admin:login')

    # Get the filter type from the query parameter
    view_mode = request.GET.get("view", "all")  # Default to 'all'

    if view_mode == "pending":
        orders = Order.objects.filter(status="pending")  # Filter for pending orders
        pending_orders_count = orders.count()
    else:
        orders = Order.objects.all()  # Fetch all orders
        pending_orders_count = None

    # Pass the orders and metrics to the template
    return render(
        request,
        "adminPages/adminorders.html",
        {
            "orders": orders,
            "view_mode": view_mode,
            "pending_orders_count": pending_orders_count,
        },
    )



def view_order(request, id):
    # Fetch the order with the given id, or return a 404 if not found
    order = get_object_or_404(Order, id=id)

    # Return the order details page
    return render(request, "adminPages/order_details.html", {"order": order})


def projects_view(request):
    projects = Project.objects.all()
    return render(request, "adminPages/adminprojects.html", {"projects": projects})


def reports_view(request):
    """Handles generating reports."""
    return render(request, "adminPages/adminreports.html")


def reports_export(request):
    """
    Export reports to CSV format.
    """
    # Example report data (replace this with actual query)
    report_data = [
        {"title": "Report 1", "details": "Details of Report 1", "created_at": "2024-12-17"},
        {"title": "Report 2", "details": "Details of Report 2", "created_at": "2024-12-18"},
    ]

    # Create the HttpResponse object with CSV headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reports.csv"'

    # Write data to CSV
    writer = csv.writer(response)
    writer.writerow(["Title", "Details", "Created At"])  # CSV Header
    for report in report_data:
        writer.writerow([report["title"], report["details"], report["created_at"]])

    return response


# Admin Inbox View
@staff_member_required
def admin_inbox(request):
    messages = Message.objects.all().order_by("-created_at")  # Ordered messages
    leads = Lead.objects.all().order_by("-created_at")  # Ordered leads

    context = {
        "messages": messages,
        "leads": leads,
        "message_count": messages.count(),  # Total messages
        "lead_count": leads.count(),  # Total leads
    }
    return render(request, "adminPages/admininbox.html", context)


# Logout View
def logout_view(request):
    """Logs the user out and redirects to the home page."""
    logout(request)
    return redirect("home")


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


@csrf_protect
def view_message(request, message_id):
    """Handles viewing a specific message."""
    # Retrieve the message by its ID or return 404 if not found
    message = get_object_or_404(Message, id=message_id)

    # Mark the message as read
    if not message.is_read:
        message.is_read = True
        message.save()

    # Render the message detail template
    return render(request, "adminPages/adminmessage_detail.html", {"message": message})


# Ensure only admin users can access this view
@csrf_protect
@staff_member_required
def admin_submit_lead(request):
    """
    Handles lead submissions for admin users.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        name = request.POST.get("name", "Anonymous")  # Default to 'Anonymous'
        phone = request.POST.get("phone", "")

        # Validate email
        if not email:
            messages.error(request, "Email is required.")
            return redirect("adminleads")

        # Validate phone number
        if phone and not re.match(r"^\+?\d{9,15}$", phone):
            messages.error(request, "Invalid phone number format.")
            return redirect("adminleads")

        # Check for duplicate email
        if Lead.objects.filter(email=email).exists():
            messages.error(request, "This email has already been submitted.")
        else:
            try:
                # Save the lead to the database
                Lead.objects.create(name=name, email=email, phone=phone)
                messages.success(request, "Lead submitted successfully!")
            except Exception as e:
                print(f"Error saving lead: {str(e)}")
                messages.error(
                    request,
                    "An error occurred while saving the lead. Please try again.",
                )

        # Redirect back to the admin leads page
        return redirect("adminleads")

    # Render the admin leads page with all leads
    leads = Lead.objects.all().order_by("-created_at")
    return render(request, "adminPages/adminleads.html", {"leads": leads})


@csrf_protect
def admin_quotes_view(request, quote_id=None):
    if request.method == "POST":
        # Handle form submission
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Quote added successfully!")
        else:
            messages.error(request, "Error adding quote. Please check the form.")

    if quote_id:
        # Show details for a specific quote
        quote = get_object_or_404(Quote, id=quote_id)
        return render(request, "adminPages/adminquotes.html", {"quote": quote})

    # List all quotes
    quotes = Quote.objects.all()
    return render(request, "adminPages/adminquotes.html", {"quotes": quotes, "form": QuoteForm()})
    

def edit_order(request, id):
    # Fetch the order by its ID or return a 404 if it doesn't exist
    order = get_object_or_404(Order, id=id)

    if request.method == "POST":
        # Process the form submission to update the order
        order.status = request.POST.get("status")  # Example field: Update order status
        # Update other fields if necessary
        order.save()

        messages.success(request, "Order successfully updated!")
        return redirect(
            "view_order", id=order.id
        )  # Redirect to the order detail page after saving

    # Render the form with the current order details
    return render(request, "adminPages/edit_order.html", {"order": order})


@login_required
@csrf_protect
def delete_message(request, message_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete this message.")
        return redirect("inbox")

    message = get_object_or_404(Message, id=message_id)
    message.delete()
    messages.success(request, "Message deleted successfully.")
    return redirect("inbox")


def order_delete(request, order_id):
    """
    Deletes a specific order by ID and redirects to the orders list.
    """
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete this order.")
        return redirect("adminorders")  # Redirect to the admin orders page

    order = get_object_or_404(Order, id=order_id)
    order.delete()
    messages.success(request, f"Order {order_id} deleted successfully.")
    return redirect("adminPages/adminorders")  # Redirect to the orders list


@staff_member_required
def delete_lead(request, lead_id):
    """
    Deletes a lead by its ID.
    """
    try:
        # Fetch the lead or raise a 404 error if it doesn't exist
        lead = get_object_or_404(Lead, id=lead_id)
        lead.delete()  # Delete the lead
        messages.success(request, "Lead deleted successfully!")
    except Exception as e:
        # Handle any exceptions (e.g., lead not found or database errors)
        messages.error(request, f"Error: {str(e)}")

    # Redirect back to admin leads page
    return redirect("adminleads")


@staff_member_required
def delete_quote(request, quote_id):
    """
    Deletes a specific quote by ID.
    """
    if request.method == "POST":
        try:
            quote = get_object_or_404(Quote, id=quote_id)
            quote.delete()
            messages.success(request, "Quote deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting quote: {e}")
        return redirect("adminquotes")
