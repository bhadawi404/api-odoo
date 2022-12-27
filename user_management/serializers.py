from rest_framework import serializers
from user_management.models import User
import xmlrpc.client

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=['username', 'db', 'url','password','company_name','location_name']
        
    
    def validate(self, attrs):
        db = attrs.get('db')
        url = attrs.get('url')
        username = attrs.get('username')
        password = attrs.get('password')
        location_name = attrs.get('location_name')
        company_name = attrs.get('company_name')
        if not password:
            raise serializers.ValidationError("Sorry Register Failed")
        return attrs

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)

