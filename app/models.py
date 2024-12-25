from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils.timezone import now


# User Registration Form
class UserCreateForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        error_messages={"exists": "This email Already Exists"},
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["placeholder"] = "User Name"
        self.fields["email"].widget.attrs["placeholder"] = "Email"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm Password"

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data["email"]).exists():
            raise forms.ValidationError(self.fields["email"].error_messages["exists"])
        return self.cleaned_data["email"]


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("in-progress", "In Progress"),
        ("completed", "Completed"),
    )

    date = models.DateField()  # Or DateTimeField, depending on requirements
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Order {self.id} - {self.status} - ${self.amount}"


# Project Model
class Project(models.Model):
    window_style = models.CharField(max_length=100)
    status = models.CharField(
        max_length=50,
        choices=(("completed", "Completed"), ("in-progress", "In Progress")),
    )

    def __str__(self):
        return self.window_style


# Quote Model
class Quote(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"


class Lead(models.Model):
    SERVICES = (
        ("window_replacement", "Window Replacement"),
        ("door_installation", "Door Installation"),
        ("roof_repair", "Roof Repair"),
    )
    STATUSES = (
        ("new", "New"),
        ("contacted", "Contacted"),
        ("converted", "Converted"),
    )

    name = models.CharField(
        max_length=100, blank=False, validators=[MinLengthValidator(2)]
    )
    email = models.EmailField(blank=False)
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                r"^\+?\d{9,15}$", "Enter a valid phone number with 9 to 15 digits."
            )
        ],
    )
    service = models.CharField(
        max_length=100, choices=SERVICES, default="window_replacement"
    )
    status = models.CharField(max_length=50, choices=STATUSES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Meta:
    ordering = ["-created_at"]
    verbose_name = "Lead"
    verbose_name_plural = "Leads"


class Message(models.Model):
    sender = models.CharField(max_length=100, verbose_name="Sender Name")  # Sender name
    receiver = models.CharField(
        max_length=100, verbose_name="Receiver Name"
    )  # Receiver name
    subject = models.CharField(
        max_length=200, verbose_name="Message Subject"
    )  # Subject of the message
    content = models.TextField(verbose_name="Message Content")  # Message content
    is_read = models.BooleanField(
        default=False, verbose_name="Read Status"
    )  # Read/unread status
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Created At"
    )  # Timestamp for creation

    class Meta:
        ordering = ["-created_at"]  # Order messages by newest first
        verbose_name = "Message"  # Friendly name in Django admin
        verbose_name_plural = "Messages"  # Plural name in Django admin

    def mark_as_read(self):
        """Mark the message as read."""
        self.is_read = True
        self.save()

    def update_read_status(self, read_status=True):
        """Update the read/unread status of the message."""
        self.is_read = read_status
        self.save()

    def __str__(self):
        return f"{self.subject} ({'Read' if self.is_read else 'Unread'})"


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ["name", "email", "phone", "details"]  # Align with model
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Customer Name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Customer Email"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Customer Phone"}
            ),
            "details": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Enter details"}
            ),
        }
