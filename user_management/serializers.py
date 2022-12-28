from rest_framework import serializers
from user_management.models import User
import xmlrpc.client

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=['email', 'db', 'url','password','company_name','location_name']
        
    
    def validate(self, attrs):
        db = attrs.get('db')
        url = attrs.get('url')
        email = attrs.get('email')
        password = attrs.get('password')
        location_name = attrs.get('location_name')
        company_name = attrs.get('company_name')
        if not password:
            raise serializers.ValidationError("Sorry Register Failed")
        return attrs

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)

class UserLoginSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    model = User
    fields = ['email', 'password']