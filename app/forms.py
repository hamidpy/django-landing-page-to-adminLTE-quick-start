from django import forms
from .models import Lead, Message, Quote  # Import your models here
from .models import Order

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["name", "email", "phone", "service", "status"]
        widgets = {
            "service": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Lead.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ["name", "email", "phone"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
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
