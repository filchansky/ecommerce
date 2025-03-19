from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django_email_verification import send_email

from .forms import LoginForm, SignUpForm, UserUpdateForm

User = get_user_model()


def sign_up_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user_email = form.cleaned_data.get('email')
            user_username = form.cleaned_data.get('username')
            user_password = form.cleaned_data.get('password1')

            # Create new user
            user = User.objects.create_user(
                username=user_username,
                email=user_email,
                password=user_password,
            )

            # Sending email
            user.is_active = False
            send_email(user)

            return redirect('account:login')
    else:
        form = SignUpForm()

    context = {
        'title': 'Sign up',
        'form': form,
    }

    return render(request, 'account/sign_up/sign_up_form.html', context)


def login_user(request):
    form = LoginForm()

    if request.user.is_authenticated:
        return redirect('shop:products')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('account:dashboard')

        messages.info(request, 'Username or password is incorrect')
        return redirect('account:login')

    context = {
        'title': 'Login',
        'form': form,
    }

    return render(request, 'account/login/login_form.html', context)


def logout_user(request):
    logout(request)
    return redirect('shop:products')


@login_required(login_url='account:login')
def dashboard_user(request):
    return render(request, 'account/dashboard/dashboard.html', {'title': 'Dashboard'})


@login_required(login_url='account:login')
def profile_user(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('account:dashboard')

    form = UserUpdateForm(instance=request.user)

    context = {
        'title': 'Profile management',
        'form': form,
    }

    return render(request, 'account/dashboard/profile_management.html', context)


@login_required(login_url='account:login')
def delete_user(request):
    user = User.objects.get(id=request.user.id)

    if request.method == 'POST':
        user.delete()
        return redirect('shop:products')

    return render(request, 'account/dashboard/account_delete.html', {'title': 'Delete account'})
