from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(user):
    token = default_token_generator.make_token(user)
    confirmation_link = f"http://yourdomain.com/api/confirm-email/{token}/"
    subject = "Email Confirmation"
    message = f"Hello {user.username},\n\nPlease confirm your email by clicking the link below:\n\n{confirmation_link}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

