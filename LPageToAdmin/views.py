from django.shortcuts import render, redirect
from app.models import UserCreateForm
from django.contrib.auth import authenticate, login


def BASE(request):
    return render(request, 'base/base.html')


def ADMINBASE(request):
    return render(request, 'base/adminbase.html')


def USERADMIN(request):
    return render(request, 'adminPages/adminhome.html')


def HOME(request):
    return render(request, 'pages/index.html')


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
