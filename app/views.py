from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth
from django.utils.timezone import now
from django.contrib.auth import logout
from app.models import Lead, Order, Project, Quote
import logging
from django import forms
from app.models import Lead  # Ensure Lead is imported
from django.contrib import messages

# Initialize logging
logger = logging.getLogger(__name__)

def USERADMIN(request):
    """
    Consolidated view for the admin dashboard.
    Displays all sidebar content below the chart on the admin page.
    """
    # Initialize metrics and data
    metrics = {
        'new_leads_count': 0,
        'pending_orders_count': 0,
        'completed_projects_count': 0,
        'monthly_revenue': 0,
        'total_quotes': 0,
        'orders_in_progress': 0,
        'sales_completed': 0,
        'popular_window_styles': [],
        'recent_leads': [],
        'sales_chart_labels': [],
        'sales_chart_data': [],
    }

    # Data containers
    all_data = {
        'leads': [],
        'orders': [],
        'quotes': [],
        'projects': [],
        'messages': [],
    }

    try:
        # Fetch metrics
        metrics['new_leads_count'] = Lead.objects.filter(status="new").count()
        metrics['pending_orders_count'] = Order.objects.filter(status="pending").count()
        metrics['completed_projects_count'] = Project.objects.filter(status="completed").count()
        metrics['monthly_revenue'] = (
            Order.objects.filter(date__month=now().month)
            .aggregate(Sum('amount'))['amount__sum']
            or 0
        )
        metrics['total_quotes'] = Quote.objects.count()
        metrics['orders_in_progress'] = Order.objects.filter(status="in-progress").count()
        metrics['sales_completed'] = Order.objects.filter(status="completed").count()

        # Popular window styles
        metrics['popular_window_styles'] = (
            Project.objects.values('window_style')
            .annotate(style_count=Count('window_style'))
            .order_by('-style_count')[:5]
        )

        # Recent leads
        metrics['recent_leads'] = Lead.objects.order_by('-created_at')[:5]

        # Sales chart data
        sales_data = (
            Order.objects.annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        metrics['sales_chart_labels'] = [f"Month {data['month']}" for data in sales_data]
        metrics['sales_chart_data'] = [data['total'] for data in sales_data]

        # Fetch all data for rendering below the chart
        all_data['leads'] = Lead.objects.all()
        all_data['orders'] = Order.objects.all()
        all_data['quotes'] = Quote.objects.all()
        all_data['projects'] = Project.objects.all()
        all_data['messages'] = Message.objects.all()

    except Exception as e:
        logger.error(f"Error fetching data in USERADMIN view: {e}")

    # Merge metrics and all_data into a single context
    context = {**metrics, **all_data}

    return render(request, 'adminPages/adminhome.html', context)

def view_message(request, message_id):
    """Handles viewing a specific message."""
    # Retrieve the message by its ID or return 404 if not found
    message = get_object_or_404(Message, id=message_id)

    # Mark the message as read
    if not message.is_read:
        message.is_read = True
        message.save()

    # Render the message detail template
    return render(request, 'adminPages/message_detail.html', {'message': message})

def leads_view(request):
    """Handles rendering the Leads page."""
    leads = Lead.objects.all()  # Fetch all leads from the database
    return render(request, 'adminPages/leads.html', {'leads': leads})

def inbox_view(request):
    """Handles rendering the Inbox page."""
    messages = Message.objects.all().order_by('-created_at')  # Fetch all messages, newest first
    return render(request, 'adminPages/inbox.html', {'messages': messages})

def orders_view(request):
    """Handles rendering the Orders page."""
    orders = Order.objects.all()  # Fetch all orders from the database
    return render(request, 'adminPages/orders.html', {'orders': orders})
class OrderForm(forms.ModelForm):
    """Form for editing an Order."""
    class Meta:
        model = Order
        fields = ['status', 'amount', 'date']

def edit_order(request, order_id):
    """Handles editing a specific order."""
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orders')  # Redirect to the orders list after saving
    else:
        form = OrderForm(instance=order)

    return render(request, 'adminPages/edit_order.html', {'form': form, 'order': order})

def view_order(request, order_id):
    """Handles viewing a specific order."""
    # Retrieve the order by its ID or return a 404 error if not found
    order = get_object_or_404(Order, id=order_id)

    # Render the order detail template
    return render(request, 'adminPages/order_detail.html', {'order': order})

def quotes_view(request):
    """Handles rendering the Quotes page."""
    quotes = Quote.objects.all()  # Fetch all quotes from the database
    return render(request, 'adminPages/quotes.html', {'quotes': quotes})

def projects_view(request):
    """Handles rendering the Projects page."""
    projects = Project.objects.all()  # Fetch all projects from the database
    return render(request, 'adminPages/projects.html', {'projects': projects})

def reports_view(request):
    """Handles rendering the Reports page."""
    # Placeholder for any data you want to display on the reports page
    context = {
        'report_data': [],  # Replace with actual report data if available
    }
    return render(request, 'adminPages/reports.html', context)

def submit_lead(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        service = request.POST.get('service')
        status = request.POST.get('status')

        # Save the lead to the database
        Lead.objects.create(
            name=name,
            email=email,
            phone=phone,
            service=service,
            status=status
        )

        # Redirect to a success page or admin dashboard
        return redirect('useradmin')  # Change 'useradmin' to your desired redirect view name

    # Render the form for GET requests
    return render(request, 'adminPages/submit_lead.html')  # Use the correct path

def logout_view(request):
    """Logs the user out and redirects to the home page."""
    logout(request)  # Logs out the user
    return redirect('home')  # Redirect to the home page after logout
