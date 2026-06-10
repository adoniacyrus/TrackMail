from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm

from apps.accounts.forms import UserRegisterForm


def register_view(request):
    """
    Handle user registration.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()

    return render(
        request,
        'registration/register.html',
        {'form': form}
    )


def login_view(request):
    """
    Handle user login with session remember logic.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Remember session logic
            remember_me = request.POST.get('remember_me')
            if remember_me:
                # 2 weeks session expiry
                request.session.set_expiry(1209600)
            else:
                # Expire session on browser close
                request.session.set_expiry(0)

            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(
        request,
        'registration/login.html',
        {'form': form}
    )


def logout_view(request):
    """
    Handle logout. Django 5.x expects POST for LogoutView, 
    but we provide a GET confirmation page and a POST submit fallback.
    """
    if request.method == 'POST':
        logout(request)
        return redirect('landing-page')

    return render(request, 'registration/logout.html')
