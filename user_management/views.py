from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from user_management.serializers import UserLoginSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate
from user_management.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
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
    db = serializer.data.get('db')
    url = serializer.data.get('url')
    
    user = authenticate(email=email, password=password, db=db, url=url)
    
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, email, password, {})
    if user is not None and uid:
      token = get_tokens_for_user(user)
      return Response({'token':token, 'msg':'Login Success','db': db}, status=status.HTTP_200_OK)
    if not uid and user is None:
      return Response({'msg':'Access Denined'}, status=status.HTTP_404_NOT_FOUND) 