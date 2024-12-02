from django.shortcuts import render, redirect
from app.models import Lead, Order, Project, Quote, UserCreateForm
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth
from django.utils.timezone import now
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from app.models import Message

def USERADMIN(request):
    unread_messages = Message.objects.filter(is_read=False).count()
    context = {
        'unread_messages': unread_messages,
    
    }
    
    return render(request, 'adminPages/adminhome.html', context)
def inbox_view(request):
    messages = Message.objects.all().order_by('-created_at')
    return render(request, 'adminPages/inbox.html', {'messages': messages})

def HOME(request):
    """Renders the homepage."""
    return render(request, 'pages/index.html')

def HOME(request):
    context = {'static_example': '/static/assets/img/testimonial-1.jpg'}
    print(context)
    return render(request, 'pages/index.html', context)

# Email utility function
def send_quote_email(to_email, subject, message):
    """Send a quote email using Django's send_mail function."""
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=False,
    )

# Base views
def BASE(request):
    return render(request, 'base/base.html')

def ADMINBASE(request):
    return render(request, 'base/adminbase.html')

def HOME(request):
    return render(request, 'pages/index.html')

# Admin Dashboard View
def USERADMIN(request):
    try:
        # Key metrics
        new_leads_count = Lead.objects.filter(status="new").count()
        pending_orders_count = Order.objects.filter(status="pending").count()
        completed_projects_count = Project.objects.filter(status="completed").count()
        monthly_revenue = (
            Order.objects.filter(date__month=now().month)
            .aggregate(Sum('amount'))['amount__sum']
            or 0
        )
        total_quotes = Quote.objects.count()
        orders_in_progress = Order.objects.filter(status="in-progress").count()
        sales_completed = Order.objects.filter(status="completed").count()
        popular_window_styles = (
            Project.objects.values('window_style')
            .annotate(style_count=Count('window_style'))
            .order_by('-style_count')[:5]
        )

        # Sales chart data
        sales_data = (
            Order.objects.annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        sales_chart_labels = [f"Month {data['month']}" for data in sales_data]
        sales_chart_data = [data['total'] for data in sales_data]

        # Recent leads
        recent_leads = Lead.objects.order_by('-created_at')[:5]
    except Exception as e:
        print(f"Error fetching data: {e}")
        new_leads_count = 0
        pending_orders_count = 0
        completed_projects_count = 0
        monthly_revenue = 0
        total_quotes = 0
        orders_in_progress = 0
        sales_completed = 0
        popular_window_styles = []
        sales_chart_labels = []
        sales_chart_data = []
        recent_leads = []

    context = {
        'new_leads_count': new_leads_count,
        'pending_orders_count': pending_orders_count,
        'completed_projects_count': completed_projects_count,
        'monthly_revenue': monthly_revenue,
        'total_quotes': total_quotes,
        'orders_in_progress': orders_in_progress,
        'sales_completed': sales_completed,
        'popular_window_styles': popular_window_styles,
        'sales_chart_labels': sales_chart_labels,
        'sales_chart_data': sales_chart_data,
        'recent_leads': recent_leads,
    }
    return render(request, 'adminPages/adminhome.html', context)

# User Registration (Signup)
def signup(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
            )
            login(request, new_user)
            return redirect('login')
    else:
        form = UserCreateForm()

    context = {
        'form': form,
    }

    return render(request, 'registration/signup.html', context)

# Quote Request View
def request_quote_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        
        subject = "Thank you for requesting a quote!"
        message = f"Hi {name},\n\nThank you for reaching out! We'll contact you soon at {phone}."
        send_quote_email(email, subject, message)

        return redirect('quote-success')
    return render(request, 'request_quote.html')

def USERADMIN(request):
    context = {
        'new_leads_count': Lead.objects.filter(status="new").count(),
        'pending_orders_count': Order.objects.filter(status="pending").count(),
        'completed_projects_count': Project.objects.filter(status="completed").count(),
        'monthly_revenue': Order.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
        'unread_messages': Message.objects.filter(is_read=False).count(),
    }
    print(context)  # Debugging
    return render(request, 'adminPages/adminhome.html', context)

def leads_view(request):
    """Handles rendering the Leads page."""
    leads = Lead.objects.all()  # Fetch all leads from the database
    return render(request, 'adminPages/leads.html', {'leads': leads})

# Sidebar Views
def leads_view(request):
    leads = Lead.objects.all()
    return render(request, 'adminPages/leads.html', {'leads': leads})

def orders_view(request):
    orders = Order.objects.all()
    return render(request, 'adminPages/orders.html', {'orders': orders})

def quotes_view(request):
    quotes = Quote.objects.all()
    return render(request, 'adminPages/quotes.html', {'quotes': quotes})

def projects_view(request):
    projects = Project.objects.all()
    return render(request, 'adminPages/projects.html', {'projects': projects})

def reports_view(request):
    # Logic for generating reports if needed
    return render(request, 'adminPages/reports.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to home after logout

