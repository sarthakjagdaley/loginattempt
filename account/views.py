from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, exceptions
from account.serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, UserChangePasswordSerializer, PasswordResetEmailSerializer, UserPasswordResetSerializer
from django.contrib.auth import authenticate
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from account.throttling import LoginThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.models import User
from account.utils import Util
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
#Generate Token manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'token' : token, 'msg' : 'Registration Successful!'},
                            status=status.HTTP_201_CREATED)            
        

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    throttle_classes = [LoginThrottle]
    
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token' : token,'msg' : 'Login Successful!'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'errors':{'non_field_errors': ['Email or Password is not Valid']}},
                status=status.HTTP_404_NOT_FOUND)
    
    def throttled(self, request, wait):    
        email = request.data.get("email")
        # print(email, "and", LoginThrottle.THROTTLE_RATES.get('loginAttempts'))
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user.is_active = False
            user.save()
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:3000/api/user/activation/'+uid+'/'+token            
            body = 'Click on below link to activate your account'+'\n'+link
            data = {
                'subject' : 'Security Alert!',
                'body' : body,
                'to_email' : user.email,
            }
            Util.send_email(data)

        raise exceptions.Throttled(detail={
            "msg":"3 Login Attempts failed! Activation link has been sent on your registered email"
        })
        
class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status = status.HTTP_200_OK)

class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self,request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context = {'user':request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg' : 'Password Changed Successfully!'}, status=status.HTTP_200_OK)
        
class PasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = PasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg' : 'Password Reset Link sent on your mail id'}, status=status.HTTP_200_OK)
        
class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, uid, token, format=None):
        print(request.data)
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
        serializer.is_valid(raise_exception=True)
        
        return Response({'msg' : 'Password Reset Successfully!'}, status=status.HTTP_200_OK)
        