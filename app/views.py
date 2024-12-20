import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt, csrf_protect  # Group csrf imports
from django.http import HttpResponseRedirect
from app.forms import OrderForm  # If OrderForm is used
from app.models import Lead, Order, Quote



from .forms import (
    LeadForm,
    QuoteForm,  # Ensure forms are used in your views
    ReplyMessageForm,
)

# Local app imports
from .models import Lead, Message, Order, Project, Quote  # Ensure no duplicates

# Initialize logging
logger = logging.getLogger(__name__)


def home(request):
    """
    Handles GET and POST requests for the landing page:
    - Saves quotes to the database
    - Sends email confirmations
    - Displays success messages
    """
    if request.method == "POST":
        # Handle form submission
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        # Ensure all fields are populated
        if not all([name, email, phone, message]):
            messages.error(request, "Please fill out all fields.")
            return render(request, "pages/index.html")

        # Save to database
        try:
            Quote.objects.create(name=name, email=email, phone=phone, message=message)
        except Exception as e:
            messages.error(request, "Failed to save your data. Please try again later.")
            print(f"Database error: {e}")
            return render(request, "pages/index.html")

        # Send email
        try:
            send_mail(
                subject="Quote Request Received",
                message=f"Thank you, {name}, for reaching out to us!",
                from_email="your-email@example.com",  # Replace with your email
                recipient_list=[email],
            )
        except Exception as e:
            messages.error(
                request, "Failed to send confirmation email. Please try again later."
            )
            print(f"Email error: {e}")
            return render(request, "pages/index.html")

        # Redirect back to the landing page with a success message
        messages.success(
            request, "Thank you for your request. We'll get back to you soon!"
        )
        return redirect("home")

    # For GET requests, render the landing page
    return render(request, "pages/index.html")


@csrf_protect
def inbox_view(request):
    """Handles rendering the Inbox page."""
    messages = Message.objects.all().order_by(
        "-created_at"
    )  # Fetch all messages, sorted by creation date
    return render(request, "adminPages/admininbox.html", {"messages": messages})


@csrf_protect
def view_order(request, order_id):
    """Handles viewing a specific order."""
    order = get_object_or_404(Order, id=order_id)
    return render(request, "adminPages/adminorder_detail.html", {"order": order})


@csrf_protect
def projects_view(request):
    """Handles rendering the Projects page."""
    projects = Project.objects.all()
    return render(request, "adminPages/adminprojects.html", {"projects": projects})


@csrf_protect
def reports_view(request):
    """Handles rendering the Reports page."""
    context = {
        "report_data": [],
    }
    return render(request, "adminPages/adminreports.html", context)


@csrf_protect
def add_message(request):
    if request.method == "POST":
        subject = request.POST.get("subject")
        body = request.POST.get("body")

        Message.objects.create(subject=subject, body=body)
        messages.success(request, "Message added successfully.")
        return redirect("inbox")


@csrf_protect
def mark_message_read(request, message_id):
    if request.method == "POST":
        message = get_object_or_404(Message, id=message_id)
        message.is_read = True
        message.save()
        messages.success(request, "Message marked as read.")
        return redirect("inbox")


@csrf_protect
def reply_message(request, message_id):
    """Handles replying to a specific message."""
    message = get_object_or_404(Message, id=message_id)
    if request.method == "POST":
        form = ReplyMessageForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user.username
            reply.receiver = message.sender
            reply.save()
            messages.success(request, "Your reply has been sent.")
            return redirect("inbox")
    else:
        form = ReplyMessageForm()
    return render(
        request,
        "adminPages/adminmessages_reply.html",
        {"form": form, "message": message},
    )


def csrf_failure(request, reason=""):
    return render(request, "csrf_failure.html", {"reason": reason})


@csrf_protect
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("useradmin")  # Replace with the appropriate redirect
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "registration/login.html")  # Ensure this template exists


# Template-based views
# About Us View
def about_page(request):
    return render(request, "pages/about.html")


def services_page(request):
    return render(request, "pages/services.html")


def contact_page(request):
    return render(request, "pages/contact.html")


# Terms of Use View
def terms_of_use_page(request):
    """Render the Terms of Use page."""
    return render(request, "pages/terms_of_use.html")


# Privacy Policy View
def privacy_policy(request):
    """Render the Privacy Policy page."""
    return render(request, "pages/privacy_policy.html")


@csrf_protect
def quote_success(request):
    return render(request, "pages/quote_success.html")  # Adjust path if necessary


@csrf_protect
def quick_lead_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        # Save email to the database as a new Lead or message
        try:
            Lead.objects.create(
                email=email, name="Anonymous"
            )  # Save email as "Anonymous"
            messages.success(
                request, "Thank you! Your email has been submitted successfully."
            )
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")

    return render(
        request, "pages/index.html"
    )  # Reload the user landing page with a success message


# Admin Login
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("admin_home")  # Redirect to admin dashboard after login
        else:
            return render(
                request, "registration/login.html", {"error": "Invalid credentials"}
            )
    return render(request, "registration/login.html")  # Render login page


@login_required  # Ensure only logged-in admins can access this view
def admin_signup(request):
    if not request.user.is_superuser:  # Only allow superusers to create new admins
        return redirect("admin_home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # Make the user an admin
            user.save()
            return redirect(
                "admin_home"
            )  # Redirect to admin dashboard after successful signup
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


def submit_lead(request):
    """
    Handles lead submissions from frontend, saves to database, and sends email confirmation.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        name = request.POST.get(
            "name", "Anonymous"
        )  # Default to 'Anonymous' if not provided
        phone = request.POST.get("phone", None)

        # Validate that email exists
        if not email:
            messages.error(request, "Email is required.")
            return redirect("home")  # Redirect to landing page

        # Check for duplicate email
        if Lead.objects.filter(email=email).exists():
            messages.error(request, "This email has already been submitted.")
            return redirect("home")

        try:
            # Save the lead to the database
            Lead.objects.create(name=name, email=email, phone=phone)

            # Send confirmation email
            subject = "Lead Submission Received"
            message = f"Dear {name},\n\nThank you for submitting your details. We'll contact you soon.\n\nPhone: {phone}"
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(subject, message, from_email, [email], fail_silently=True)

            # Success message
            messages.success(
                request, "Thank you! Your details have been submitted successfully."
            )
            return redirect("home")  # Redirect back to landing page
        except Exception as e:
            print(f"Error saving lead or sending email: {e}")
            messages.error(request, "An error occurred. Please try again later.")
            return redirect("home")

    # Render the landing page if GET request
    return render(request, "pages/index.html")


def request_quote(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your quote request has been submitted!")
            return redirect("home")  # Redirect to home page after submission
        else:
            messages.error(request, "There was an error submitting your request.")
    else:
        form = QuoteForm()
    
    return render(request, "pages/request_quote.html", {"form": form})


# Admin Logout
@csrf_protect
def admin_logout(request):
    logout(request)  # Use Django's auth logout
    return redirect("admin_login")  # Redirect to admin login page
