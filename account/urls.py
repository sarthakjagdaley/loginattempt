from django.urls import path
from django.contrib import admin
from account.views import UserRegistrationView, UserLoginView, UserProfileView, UserChangePasswordView, PasswordResetEmailView, UserPasswordResetView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name = 'register'),
    path('login/', UserLoginView.as_view(), name = 'login'),
    path('profile/',UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('reset-password-email/',PasswordResetEmailView.as_view(), name='reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password')
]
