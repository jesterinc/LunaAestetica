# login/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from login.models import Users
import uuid

class UserRegistrationSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True)
  phone = serializers.CharField(write_only=True)

  class Meta:
    model = User
    fields = ['username', 'email', 'password', 'phone', 'first_name', 'last_name']

  def create(self, validated_data):

    phone = validated_data.pop('phone')
    user = User.objects.create_user(**validated_data)
    Users.objects.update_or_create(user=user,defaults={'phone': phone,'token': str(uuid.uuid4()),'active': True})
    return user
