from dataclasses import fields
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class SignUpSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('first_name', 'last_name', 'email', 'password')

    extra_kwargs = {
      'first_name': { 'required': True, 'allow_blank': False },
      'last_name': { 'required': True, 'allow_blank': False },
      'email': { 'required': True, 'allow_blank': False },
      'password': { 'required': True, 'allow_blank': False, 'min_length': 6 },
    }

class UserSerializer(serializers.ModelSerializer):
  id = serializers.UUIDField(source='userprofile.id')
  firstTimeVisaApplication = serializers.BooleanField(source='userprofile.firstTimeVisaApplication')
  phoneNumber = serializers.IntegerField(source='userprofile.phoneNumber')
  medicalCondition = serializers.BooleanField(source='userprofile.medicalCondition')
  medicalConditionDescription = serializers.CharField(source='userprofile.medicalConditionDescription')
  married = serializers.BooleanField(source='userprofile.married')
  religion = serializers.ChoiceField(choices=UserProfile._meta.get_field('religion').choices, source='userprofile.religion')
  gender = serializers.ChoiceField(choices=UserProfile._meta.get_field('gender').choices, source='userprofile.gender')
  resume = serializers.CharField(source='userprofile.resume')
  academicPapers = serializers.CharField(source='userprofile.academicPapers')
  bankStatements = serializers.CharField(source='userprofile.bankStatements')
  class Meta:
    model = User
    fields = (
      'id',
      'first_name', 
      'last_name',
      'email', 
      'username',
      'phoneNumber',
      'firstTimeVisaApplication', 
      'medicalCondition', 
      'medicalConditionDescription',
      'married',
      'religion',
      'gender',
      'resume', 
      'academicPapers', 
      'bankStatements'
    )