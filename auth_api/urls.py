from django.urls import path
from .views import RegisterView, EmailConfirmationView, CompleteProfileView, LoginView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='account_signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('complete-profile/', CompleteProfileView.as_view(), name='complete_profile'),
]
