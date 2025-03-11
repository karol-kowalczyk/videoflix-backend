from django.urls import path
from .views import RegisterView, LoginView, CheckEmailView, ResetPasswordView, ActivateAccountView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('check-email/', CheckEmailView.as_view(), name='check-email'),
    path('reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('activate-account/<str:token>/', ActivateAccountView.as_view(), name='activate-account'),
]
