from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.urls import path, reverse_lazy

from .views import dashboard_user, delete_user, login_user, logout_user, profile_user, sign_up_user

app_name = 'account'

urlpatterns = [
    # Registration & email verification
    path('signup/', sign_up_user, name='sign-up'),
    path(
        'email-verification-sent/',
        lambda request: render(request, 'account/email/email_verification_sent.html'),
        name='email-verification-sent',
    ),

    # Login & logout
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),

    # Dashboard
    path('dashboard/', dashboard_user, name='dashboard'),
    path('profile-management/', profile_user, name='profile-management'),
    path('delete-user/', delete_user, name='delete-user'),

    # Reset password
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='account/password/password_reset.html',
            email_template_name='account/password/password_reset_email.html',
            success_url=reverse_lazy('account:password-reset-done'),
        ),
        name='password-reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='account/password/password_reset_done.html',
        ),
        name='password-reset-done',
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='account/password/password_reset_confirm.html',
            success_url=reverse_lazy('account:password-reset-complete'),
        ),
        name='password-reset-confirm',
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='account/password/password_reset_complete.html',
        ),
        name='password-reset-complete',
    ),
]
