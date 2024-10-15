from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from .serializers import RegisterSerializer, CompleteProfileSerializer, LoginSerializer, UserProfileSerializer
from allauth.account.utils import send_email_confirmation
from allauth.account.models import EmailConfirmation
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .models import OTP
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone




class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            otp = OTP.generate_otp(user)
            self.send_otp_email(user.email, otp.code)
            return Response({
                "message": "OTP sent to your email for verification."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_otp_email(self, email, otp_code):
        subject = 'Your OTP for Registration'
        message = f'Your OTP is: {otp_code}. It will expire in 10 minutes.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

# class EmailConfirmationView(APIView):
#     def post(self, request, *args, **kwargs):
#         key = request.data.get('key')
#         if not key:
#             return Response({'message': 'Confirmation key is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             confirmation = EmailConfirmation.objects.get(key=key)
#             confirmation.confirm(request)
#             return Response({'message': 'Your email has been confirmed successfully.'}, status=status.HTTP_200_OK)
#         except EmailConfirmation.DoesNotExist:
#             return Response({'message': 'Invalid confirmation key or expired link.'}, status=status.HTTP_400_BAD_REQUEST)



class OTPVerificationView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')
        
        if not email or not otp_code:
            return Response({'message': 'Email and OTP code are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            User = get_user_model()
            user = User.objects.get(email=email)
            
            # Instead of querying with 'is_valid', check the expiration time
            otp = OTP.objects.filter(
                user=user,
                code=otp_code,
                expires_at__gt=timezone.now()
            ).first()
            
            if otp:
                # OTP is valid
                user.is_verified = True
                user.is_active = True  # Set is_active to True
                user.save()
                otp.delete()  # Remove the used OTP
                return Response({'message': 'Your email has been verified successfully.'}, status=status.HTTP_200_OK)
            else:
                # OTP is invalid or expired
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)

                if not user.is_profile_completed:
                    return Response({
                        'message': 'Login successful, but please complete your profile',
                        'token': token.key,
                        'link': f"{request.get_host()}/complete-profile/"
                    }, status=status.HTTP_200_OK)
                
                
                return Response({
                    'message': 'Login successful',
                    'token': token.key,
                    'email': user.email,
                    'profile_completed': True
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Debug: Print authentication information
            # print(f"User: {request.user}")
            # print(f"Auth: {request.auth}")
            # print(f"Request headers: {request.headers}")
            # print(f"Authentication classes: {self.authentication_classes}")

            serializer = CompleteProfileSerializer(instance=request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Profile completed successfully.",
                    "profile": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AuthenticationFailed as e:
            print(f"Authentication failed: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully.",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({
            "message": "Profile deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)







