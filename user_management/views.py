from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from user_management.serializers import UserLoginSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate
from user_management.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
import xmlrpc.client

# Generate Token Manually
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
    return Response({'token':token, 'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')

    
    user = authenticate(email=email, password=password)
    
    
    if user is not None:
      print(user.url,"==masuk s===")
      common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(user.url))
      uid = common.authenticate(user.db, email, password, {})
      if uid:
        token = get_tokens_for_user(user)
        return Response({'token':token, 'msg':'Login Success', 'user_id':user.id}, status=status.HTTP_200_OK)
      if not uid:
        return Response({'msg':'Tidak Terdaftar di amtiss'}, status=status.HTTP_404_NOT_FOUND) 
    if user is None:
      return Response({'msg':'email or password is valid'}, status=status.HTTP_404_NOT_FOUND) 