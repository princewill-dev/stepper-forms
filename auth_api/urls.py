from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='account_signup'),
    path('otp-verification/', OTPVerificationView.as_view(), name='otp_verification'),
    path('login/', LoginView.as_view(), name='login'),
    path('complete-profile/', CompleteProfileView.as_view(), name='complete_profile'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('update-profile/', UpdateProfileView.as_view(), name='update_profile'),
    path('delete-profile/', DeleteProfileView.as_view(), name='delete_profile'),
]