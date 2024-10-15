from rest_framework import serializers
from .models import CustomUser
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.account.models import EmailAddress, EmailConfirmation
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = get_adapter().new_user(self.context['request'])
        user.email = validated_data.get('email')
        user.set_password(validated_data.get('password'))
        user.is_active = False
        user.save()
        
        # Create EmailAddress instance
        email_address = EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
        
        # Create EmailConfirmation instance
        confirmation = EmailConfirmation.create(email_address)
        
        # Send confirmation email
        confirmation.send(self.context['request'])
        
        return user
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                if not user.is_active:
                    raise serializers.ValidationError("User account is not active.")
                data['user'] = user
                return data
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")


class CompleteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'address', 'country', 'city', 'postal_code']
        extra_kwargs = {
            'phone_number': {'required': True},
            'country': {'required': True},
            'address': {'required': True},
            'city': {'required': True},
            'postal_code': {'required': True},
        }

    def validate(self, data):
        if not data.get('phone_number') or not data.get('country') or not data.get('address') or not data.get('city') or not data.get('postal_code'):
            raise serializers.ValidationError("Phone number, country, address, city, and postal code are required.")
        return data




