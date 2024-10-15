from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    def confirm_email(self, request, email_address):
        # Call the parent class's confirm_email method
        super().confirm_email(request, email_address)
        
        # Set is_active to True
        user = email_address.user
        user.is_active = True
        user.save()

