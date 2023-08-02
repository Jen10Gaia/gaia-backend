from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .validators import validate_file_extension
from .serializers import SignUpSerializer, UserSerializer



# Create your views here.
@api_view(['POST'])
def register(request):
  data = request.data
  user = SignUpSerializer(data=data)

  if user.is_valid():
    if not User.objects.filter(username=data['email']).exists():
      user = User.objects.create(
        first_name = data['first_name'],
        last_name = data['last_name'],
        username = data['email'],
        email = data['email'],
        password = make_password(data['password'])
      ) 

      return Response({
        'message': 'User registered.'},
        status=status.HTTP_200_OK
      )
    else:
      return Response({
        'error': 'User already exists'},
        status=status.HTTP_400_BAD_REQUEST
      )

  else:
    return Response(user.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def currentUser(request):

  user = UserSerializer(request.user)

  return Response(user.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request):
  user = request.user

  data = request.data

  user.first_name = data['first_name']
  user.last_name = data['last_name']
  user.username = data['email']
  user.email = data['email']

  if data['password'] != '':
    user.password = make_password(data['password'])

  user.save()

  serializer = UserSerializer(user, many=False)
  return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def uploadResume(request):

  user = request.user
  resume = request.FILES['resume']

  if resume == '':
      return Response({ 'error': 'Please upload your resume.' }, status=status.HTTP_400_BAD_REQUEST)

  isValidFile = validate_file_extension(resume.name)

  if not isValidFile:
      return Response({ 'error': 'Please upload only pdf file.' }, status=status.HTTP_400_BAD_REQUEST)

  serializer = UserSerializer(user, many=False)

  user.userprofile.resume = resume
  user.userprofile.save()

  return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def uploadAcademicPapers(request):

  user = request.user
  academicPapers = request.FILES['academicPapers']

  if academicPapers == '':
      return Response({ 'error': 'Please upload your academic credentials.' }, status=status.HTTP_400_BAD_REQUEST)

  isValidFile = validate_file_extension(academicPapers.name)

  if not isValidFile:
      return Response({ 'error': 'Please upload only pdf file.' }, status=status.HTTP_400_BAD_REQUEST)

  serializer = UserSerializer(user, many=False)

  user.userprofile.academicPapers = academicPapers
  user.userprofile.save()

  return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def uploadBankStatements(request):

  user = request.user
  bankStatements = request.FILES['bankStatements']

  if bankStatements == '':
      return Response({ 'error': 'Please upload your bank statements for the last 6 months.' }, status=status.HTTP_400_BAD_REQUEST)

  isValidFile = validate_file_extension(bankStatements.name)

  if not isValidFile:
      return Response({ 'error': 'Please upload only pdf file.' }, status=status.HTTP_400_BAD_REQUEST)

  serializer = UserSerializer(user, many=False)

  user.userprofile.bankStatements = bankStatements
  user.userprofile.save()

  return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
  user = request.user
  phoneNumber = request.POST.get('phoneNumber')
  firstVisaApplication = request.POST.get('firstVisaApplication')
  medicalCondition = request.POST.get('medicalCondition')
  medicalConditionDescription = request.POST.get('medicalConditionDescription')
  married = request.POST.get('married')
  religion = request.POST.get('religion')
  gender = request.POST.get('gender')

  serializer = UserSerializer(user, many=False)

  user.userprofile.phoneNumber = phoneNumber
  user.userprofile.firstVisaApplication = firstVisaApplication
  user.userprofile.medicalCondition = medicalCondition
  user.userprofile.medicalConditionDescription = medicalConditionDescription
  user.userprofile.married = married
  user.userprofile.religion = religion
  user.userprofile.gender = gender
  user.userprofile.save()

  return Response(serializer.data)


# Dashboard Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def isAdminCheck(request):  
  
  user = request.user
  isAdmin = user.is_superuser
  
  if isAdmin:
    return Response({'isAdmin': True})
  else:
    return Response({'isAdmin': False})
  
 

@api_view(['GET'])
def getAllUsers(request):
  # Get all users
  users = User.objects.all()
  userCount = users.count()

  # Get the number of new users
  lastWeek = timezone.now() - timezone.timedelta(days=7)
  newUsers = User.objects.filter(date_joined__gte=lastWeek).count()

  # Serialize the users data
  serializer = UserSerializer(users, many=True)
  
  data = {
      'users': serializer.data,
      'userCount': userCount,
      'newUsers': newUsers
  }

  return Response(data)







