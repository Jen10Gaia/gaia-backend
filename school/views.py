import uuid
import stripe
import os
import dotenv

from django.conf import settings
from django.shortcuts import render
from django.db.models import Avg, Min, Max, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.mail import send_mail


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from utils.custom_functions import can_user_modify_service

from .models import School, CandidatesApplied, Status
from .filters import SchoolsFilter
from .serializers import SchoolSerializer, CandidatesAppliedSerializer

# Create your views here.

@api_view(['GET'])
def getAllSchools(request):
  filterset = SchoolsFilter(request.GET, queryset=School.objects.all().order_by('id'))

  count = filterset.qs.count()

  # Pagination
  resPerPage = 3

  paginator = PageNumberPagination()
  paginator.page_size = resPerPage

  queryset = paginator.paginate_queryset(filterset.qs, request)

  serializer = SchoolSerializer(queryset, many=True)
  return Response({
    "count": count,
    "resPerPage": resPerPage,
    'schools': serializer.data
    })


@api_view(['GET'])
def getSchool(request, pk):
  school = get_object_or_404(School, id=pk)

  candidates = school.candidatesapplied_set.all().count()

  serializer = SchoolSerializer(school, many=False)

  return Response({'school':serializer.data, 'candidates':candidates})
 


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def newSchool(request):
  currentUser = request.user
  request.data['user'] = currentUser
  data = request.data

  school = School.objects.create(**data)

  serializer = SchoolSerializer(school, many=False)
  return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def updateSchool(request, pk):
  school = get_object_or_404(School, id=pk)

  # Check if the user can update the service
  response = can_user_modify_service(school, request)
  if response:
    return response

  school.title = request.data['title']
  school.description = request.data['description']
  school.email = request.data['email']
  school.address = request.data['address']
  school.scholarshipType = request.data['scholarshipType']
  school.educationLevel = request.data['educationLevel']
  school.country = request.data['country']
  school.course = request.data['course']
  school.tuitionFee = request.data['fee']
  school.positions = request.data['positions']
  school.price = request.data['price']

  school.save()

  serializer = SchoolSerializer(school, many=False)

  return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def deleteSchool(request, pk):
  school = get_object_or_404(School, id=pk)

  # Check if the user can update the service
  response = can_user_modify_service(school, request)
  if response:
    return response

  school.delete()

  return Response({ 'message': 'School is Deleted.' }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getTopicStats(request, topic):
  args = { 'title__icontains': topic }
  schools = School.objects.filter(**args)

  if len(schools) == 0:
      return Response({ 'message': 'Not stats found for {topic}'.format(topic=topic) })

  
  stats = schools.aggregate(
      total_schools = Count('title'),
      avg_positions = Avg('positions'),
      avg_fee = Avg('fee'),
      min_fee = Min('fee'),
      max_fee = Max('fee')
  )

  return Response(stats)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def applyToSchool(request, pk):

    user = request.user
    school = get_object_or_404(School, id=pk)

    if user.userprofile.resume == '':
      return Response({ 'error': 'Please upload your resume first' }, status=status.HTTP_400_BAD_REQUEST)
    
    if user.userprofile.academicPapers == '':
      return Response({ 'error': 'Please upload your academic documents first' }, status=status.HTTP_400_BAD_REQUEST)
    
    if user.userprofile.bankStatements == '':
      return Response({ 'error': 'Please upload your bank statements first' }, status=status.HTTP_400_BAD_REQUEST)

    if school.lastDate < timezone.now():
      return Response({ 'error': 'You can not apply to this school. Deadline passed.' }, status=status.HTTP_400_BAD_REQUEST)

    alreadyApplied = school.candidatesapplied_set.all().filter(user=user).exists()

    if alreadyApplied:
      return Response({ 'error': 'You have already applied to this school.' }, status=status.HTTP_400_BAD_REQUEST)


    schoolApplied = CandidatesApplied.objects.create( 
      school = school,
      user = user,
      resume = user.userprofile.resume,
      academicPapers = user.userprofile.academicPapers,
      bankStatements = user.userprofile.bankStatements,
    )

    return Response({
      'applied': True,
      'school_id': schoolApplied.id
    },
    status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCurrentUserAppliedSchools(request):

    args = { 'user_id': request.user.id }

    schools = CandidatesApplied.objects.filter(**args)

    serializer = CandidatesAppliedSerializer(schools, many=True)

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def isApplied(request, pk):

  user = request.user
  school = get_object_or_404(School, id=pk)

  # applied = school.school_candidate_application.filter(user=user).exists()
  applied = school.candidatesapplied_set.filter(user=user).exists()

  return Response(applied)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCurrentUserSchools(request):

  args = { 'user': request.user.id }

  schools = School.objects.filter(**args)
  serializer = SchoolSerializer(schools, many=True)

  return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCandidatesApplied(request, pk):

  user = request.user
  school = get_object_or_404(School, id=pk)

  if school.user != user:
    return Response({ 'error': 'You can not access this school' }, status=status.HTTP_403_FORBIDDEN)

  candidates = school.candidatesapplied_set.all()
  #candidates = school.school_candidate_application.all()

  serializer = CandidatesAppliedSerializer(candidates, many=True)

  return Response(serializer.data)



# Payments and other


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def approveApplication(request, pk):
  candidate = get_object_or_404(CandidatesApplied, id=pk)

  # Approve Candidates Application
  if candidate.approved:
      return Response({'message': 'This application has already been approved.'}, status=400)
  
  candidate.approved = True
  candidate.status = Status.Approved
  candidate.save()

  # Reject Remaining Candidates
  school = candidate.school
  approvedCount = CandidatesApplied.objects.filter(school=school, approved=True).count()
  if approvedCount >= school.positions:
      #Reject all other candidates who have applied to this job
    candidates_to_reject = CandidatesApplied.objects.filter(school=school, approved=False)
    for candidate in candidates_to_reject:
      candidate.rejected = True
      candidate.status = Status.Rejected
      candidate.save()

  
  # Update Positions Left
  positionsLeft = school.positions - approvedCount
  
  return Response({
      'positionsLeft': positionsLeft,
      'status': candidate.status,
      'approved': True,
      'application_id': candidate.school.id,
      'user_id': candidate.user.id,
      'message': 'Application approved successfully.'
  }, status=status.HTTP_200_OK)

 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def isApproved(request, pk):
    candidate = get_object_or_404(CandidatesApplied, id=pk,)
    isApproved = candidate.approved
    candidateStatus = Status.Approved

    return Response({'isApproved':isApproved, 'status':candidate})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def isRejected(request, pk):
    candidate = get_object_or_404(CandidatesApplied, id=pk,)
    isRejected = candidate.rejected
    candidateStatus = Status.Rejected

    return Response({'isRejected': isRejected, 'status':candidateStatus})


@api_view(['GET'])
def approved_count(request):
    count = CandidatesApplied.objects.filter(approved=True).count()
    return Response({'count': count})

@api_view(['GET'])
def isSchoolFull(request, school_id):
    school = School.objects.get(id=school_id)
    is_full = school.isSchoolfull()
    data = {'is_full': is_full}
    return Response(data)

@api_view(['GET'])
def checkPositionsLeft(request, school_id):
    school = School.objects.get(id=school_id)
    approved_count = CandidatesApplied.objects.filter(school=school, approved=True).count()
    positionsLeft = school.positions - approved_count
    data = {'positions_left': positionsLeft}
    return Response(data)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def markCandidateAsPaid(request, pk):
  user = request.user
  candidate = get_object_or_404(CandidatesApplied, id=pk)

  # Mark the candidate as paid and save the candidate
  candidate.paid = True
  candidate.save()

  # You may return additional data as needed
  serializer = CandidatesAppliedSerializer(candidate)
  return Response({'paid':candidate.paid})

  

############################# DASHBOARD #############################

#ORDERS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orders(request):
   
    # Filter candidates who have paid for the job
    paidCandidates = CandidatesApplied.objects.filter(paid=True)
    
    # Get the count of paid candidates
    paidCount = paidCandidates.count()
    
    # Serialize the data and return response
    serializer = CandidatesAppliedSerializer(paidCandidates, many=True)
    data = {'ordersCount': paidCount, 'paidCandidates': serializer.data}
    return Response(data=data, status=status.HTTP_200_OK)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def revenue(request):
    
    # Get all paid candidates for the job
    paidCandidates = CandidatesApplied.objects.filter( paid=True)
    
    # Calculate total revenue from all paid candidates
    totalRevenue = sum(candidate.school.price for candidate in paidCandidates)

    # Get paid candidates within the last week
    lastWeek = timezone.now() - timezone.timedelta(days=7)
    recentPaidCandidates = paidCandidates.filter(appliedAt__gte=lastWeek)
    
    # Calculate total revenue from recent paid candidates
    recentRevenue = sum(candidate.school.price for candidate in recentPaidCandidates)
    
    # Calculate percentage increase in revenue
    if totalRevenue == 0:
        percentIncrease = 0
    else:
        percentIncrease = round(((recentRevenue - totalRevenue) / totalRevenue) * 100, 2)
    
    # Get the count of paid candidates
    paidCount = paidCandidates.count()
    
    # Serialize the data and return response
    serializer = CandidatesAppliedSerializer(paidCandidates, many=True)
    data = {
        'totalRevenue': totalRevenue,
        'recentRevenue': recentRevenue,
        'percentIncrease': percentIncrease,
        'candidates': serializer.data, 
    }
    return Response(data=data, status=status.HTTP_200_OK)
    

