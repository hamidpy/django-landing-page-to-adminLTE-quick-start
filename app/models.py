from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

# User Registration Form
class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email', error_messages={'exists': 'This email Already Exists'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError(self.fields['email'].error_messages['exists'])
        return self.cleaned_data['email']

# Order Model
class Order(models.Model):
    status = models.CharField(
        max_length=50, 
        choices=(
            ('pending', 'Pending'), 
            ('in-progress', 'In Progress'), 
            ('completed', 'Completed')
        )
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"Order {self.id} - {self.status}"

# Project Model
class Project(models.Model):
    window_style = models.CharField(max_length=100)
    status = models.CharField(
        max_length=50, 
        choices=(
            ('completed', 'Completed'), 
            ('in-progress', 'In Progress')
        )
    )

    def __str__(self):
        return self.window_style

# Quote Model
class Quote(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quote Request from {self.name}"

# Lead Model
class Lead(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    service = models.CharField(max_length=100)
    status = models.CharField(
        max_length=50, 
        choices=(
            ('new', 'New'), 
            ('contacted', 'Contacted'), 
            ('converted', 'Converted')
        )
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} from {self.sender}"
