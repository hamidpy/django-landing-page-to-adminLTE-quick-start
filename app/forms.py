from django import forms
from .models import Lead, Message, Quote  # Import your models here
from .models import Order
from app.models import Lead  # Ensure this imports the correct Lead model


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["name", "email", "phone"]  # Specify fields to include in the form

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Lead.objects.filter(email=email).exists():
            raise forms.ValidationError("This email has already been submitted.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")  # Fetch the phone field value
        if not phone:  # If phone is empty or None, skip validation
            return phone

        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")

        if len(phone) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits long.")

        return phone


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ["name", "email", "phone", "details"]  # Use existing fields in Quote model
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Customer Name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Customer Email"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Customer Phone"}),
            "details": forms.Textarea(attrs={"class": "form-control", "placeholder": "Additional Details"}),
        }


class ReplyMessageForm(forms.Form):
    subject = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    content = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}))


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["date", "amount", "status"]  # Ensure these fields match the model
