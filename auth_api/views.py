from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, CompleteProfileSerializer, LoginSerializer, UserProfileSerializer
from allauth.account.utils import send_email_confirmation
from allauth.account.models import EmailConfirmation
from rest_framework.exceptions import ValidationError, AuthenticationFailed




class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            send_email_confirmation(request, user, signup=True)
            return Response({"message": "Verification email sent."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailConfirmationView(APIView):
    def post(self, request, *args, **kwargs):
        key = request.data.get('key')
        if not key:
            return Response({'message': 'Confirmation key is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            confirmation = EmailConfirmation.objects.get(key=key)
            confirmation.confirm(request)
            return Response({'message': 'Your email has been confirmed successfully.'}, status=status.HTTP_200_OK)
        except EmailConfirmation.DoesNotExist:
            return Response({'message': 'Invalid confirmation key or expired link.'}, status=status.HTTP_400_BAD_REQUEST)
        
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






