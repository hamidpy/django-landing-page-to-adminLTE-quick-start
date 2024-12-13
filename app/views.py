
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


def HOME(request):
    """Renders the landing page."""
    return render(request, "pages/index.html")

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


@csrf_protect
def inbox_view(request):
    """Handles rendering the Inbox page."""
    messages = Message.objects.all().order_by(
        "-created_at"
    )  # Fetch all messages, sorted by creation date
    return render(request, "adminPages/admininbox.html", {"messages": messages})


@csrf_protect
def orders_view(request):
    """Handles rendering the Orders page."""
    orders = Order.objects.all()
    return render(request, "adminPages/adminorders.html", {"orders": orders})


@csrf_protect
def edit_order(request, order_id):
    """Handles editing a specific order."""
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect("orders")
    else:
        form = OrderForm(instance=order)
    return render(
        request, "adminPages/adminedit_order.html", {"form": form, "order": order}
    )


@csrf_protect
def view_order(request, order_id):
    """Handles viewing a specific order."""
    order = get_object_or_404(Order, id=order_id)
    return render(request, "adminPages/adminorder_detail.html", {"order": order})


@csrf_protect
def quotes_view(request):
    """Handles rendering the Quotes page."""
    quotes = Quote.objects.all()
    return render(request, "adminPages/adminquotes.html", {"quotes": quotes})


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


from django.http import HttpResponseRedirect

def submit_lead(request):
    """Handles submission of a lead from the landing page."""
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            # Save the form and print the submitted data
            form.save()
            form_data = request.POST  # Extract form data for debugging
            print("Lead submitted:", form_data)  # Debug statement to log the form data
            
            # Redirect to success page
            return HttpResponseRedirect('/')  # Redirect to the landing page
        else:
            # Handle invalid form data by re-rendering the form with errors
            return render(request, "pages/index.html", {"form": form})
    else:
        # Render the form for GET requests
        form = LeadForm()
        return render(request, "pages/index.html", {"form": form})


@csrf_protect
def submit_quote(request):
    if request.method == "POST":
        # Use the QuoteForm to validate and save data
        form = QuoteForm(request.POST)
        if form.is_valid():
            try:
                # Save the form data to the database
                quote = form.save()

                # Success message
                messages.success(
                    request, "Your quote request has been submitted successfully!"
                )

                # Send email notification
                try:
                    send_mail(
                        "New Quote Request",
                        f"Name: {quote.name}\nEmail: {quote.email}\nPhone: {quote.phone}",
                        "windowupgrades4u@gmail.com",  # From email
                        ["paparayoncheck@gmail.com"],  # To email
                    )
                except Exception as e:
                    logger.error(f"Error sending email: {e}")
                    messages.warning(
                        request,
                        "Your quote was submitted, but we couldn't send a notification.",
                    )

                return redirect("/")  # Redirect to homepage or confirmation page
            except Exception as e:
                logger.error(f"Error saving quote: {e}")
                messages.error(request, f"Error submitting quote: {e}")
        else:
            messages.error(
                request,
                "There was an error with your submission. Please correct the errors below.",
            )
    else:
        form = QuoteForm()  # Display an empty form for GET requests

    # Pass the form to the template
    return render(request, "pages/submit_quote.html", {"form": form})


@csrf_protect
def add_message(request):
    if request.method == "POST":
        subject = request.POST.get("subject")
        body = request.POST.get("body")

        Message.objects.create(subject=subject, body=body)
        messages.success(request, "Message added successfully.")
        return redirect("inbox")


@csrf_protect
def delete_message(request, message_id):
    try:
        Message.objects.get(id=message_id).delete()
        messages.success(request, "Message deleted successfully.")
    except Message.DoesNotExist:
        messages.error(request, "Message not found.")
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
def admin_submit_lead(request):
    if request.method == "POST":
        # Handle admin-specific logic for lead submission
        ...
    return render(request, "adminPages/submit_lead.html")


@csrf_protect
def admin_quotes_view(request):
    quotes = Quote.objects.all()  # Fetch all quotes
    return render(request, "adminPages/adminquotes.html", {"quotes": quotes})


# views.py
def request_quote_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        name = request.POST.get("name", "Anonymous")  # Default to "Anonymous"
        phone = request.POST.get("phone", None)  # Optional field

        if Quote.objects.filter(email=email).exists():
            messages.error(
                request, "This email has already been used to submit a quote."
            )
        else:
            try:
                # Save the quote
                Quote.objects.create(email=email, name=name, phone=phone)
                # Redirect to the success page after processing the form
                return redirect("quote-success")
            except IntegrityError:
                messages.error(
                    request,
                    "There was an error processing your request. Please try again.",
                )

        return redirect("quote-success")  # Redirect to the success page
    return render(request, "pages/request_quote.html")  # Render the form page


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


@csrf_protect
# Public Landing Page (Generic)
def index(request):
    """Renders the landing page with a form for users and a login link for admins."""
    if request.method == "POST":
        # Handle form submission for window replacement
        # Form processing logic here (if applicable)
        pass
    return render(request, "pages/index.html")


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


def admin_leads_view(request):
    leads = Lead.objects.all()  # Fetch all leads from the database
    return render(request, "adminPages/adminleads.html", {"leads": leads})


def admin_submit_lead_view(request):
    # Logic for handling lead submissions by admins
    if request.method == "POST":
        # Handle form submission
        pass
    return render(request, "adminPages/adminsubmitlead.html")


def admin_leads(request):
    """Render the admin Leads page."""
    leads = Lead.objects.all()  # Fetch all lead objects from the database
    return render(
        request, "adminPages/adminleads.html", {"leads": leads}
    )  # Ensure this template path is correct


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


# Admin Logout
@csrf_protect
def admin_logout(request):
    logout(request)  # Use Django's auth logout
    return redirect("admin_login")  # Redirect to admin login page
