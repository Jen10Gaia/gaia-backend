import os
import uuid
import stripe
import dotenv
import requests
import json

from django.conf import settings
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Min, Max, Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.mail import send_mail

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from utils.custom_functions import can_user_modify_service

from .models import Job, CandidatesApplied, Status
from .filters import JobsFilter
from .serializers import JobSerializer, CandidatesAppliedSerializer


# This is your test secret API key.
stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

# Create your views here.
@api_view(['GET'])
def getAllJobs(request):
  filterset = JobsFilter(request.GET, queryset=Job.objects.all().order_by('id'))

  count = filterset.qs.count()

  # Pagination
  resPerPage = 3

  paginator = PageNumberPagination()
  paginator.page_size = resPerPage

  queryset = paginator.paginate_queryset(filterset.qs, request)


  serializer = JobSerializer(queryset, many=True)
  return Response({
    "count": count,
    "resPerPage": resPerPage,
    'jobs': serializer.data
  })


@api_view(['GET'])
def getJob(request, pk):
  job = get_object_or_404(Job, id=pk)

  candidates = job.candidatesapplied_set.all().count()

  serializer = JobSerializer(job, many=False)

  return Response({'job':serializer.data, 'candidates':candidates})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def newJob(request):
  currentUser = request.user
  request.data['user'] = currentUser
  data = request.data

  job = Job.objects.create(**data)

  serializer = JobSerializer(job, many=False)
  return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def updateJob(request, pk):
  job = get_object_or_404(Job, id=pk)

  # Check if the user can update the service
  response = can_user_modify_service(job, request)
  if response:
    return response

  job.title = request.data['title']
  job.description = request.data['description']
  job.email = request.data['email']
  job.address = request.data['address']
  job.jobType = request.data['jobType']
  job.country = request.data['country']
  job.education = request.data['education']
  job.industry = request.data['industry']
  job.experience = request.data['experience']
  job.salary = request.data['salary']
  job.positions = request.data['positions']
  job.company = request.data['company']
  job.price = request.data['price']
 

  job.save()

  serializer = JobSerializer(job, many=False)

  return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def deleteJob(request, pk):
  job = get_object_or_404(Job, id=pk)
  # Check if the user can update the service
  response = can_user_modify_service(job, request)

  if response:
    return response

  job.delete()

  return Response({ 'message': 'Job is Deleted.' }, status=status.HTTP_200_OK)


@api_view(['GET'])
def getTopicStats(request, topic):
  # Checks if the title contains the topic
  args = { 'title__icontains': topic }
  jobs = Job.objects.filter(**args)

  if len(jobs) == 0:
    return Response({ 'message': 'Not stats found for {topic}'.format(topic=topic) })

  
  stats = jobs.aggregate(
    total_jobs = Count('title'),
    avg_positions = Avg('positions'),
    avg_salary = Avg('salary'),
    min_salary = Min('salary'),
    max_salary = Max('salary')        
  )

  return Response(stats)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def applyToJob(request, pk):

    user = request.user
    job = get_object_or_404(Job, id=pk)

    if user.userprofile.resume == '' or user.userprofile.academicPapers == '' or user.userprofile.bankStatements == '':
      return Response({ 'error': 'Please upload all required documents first' }, status=status.HTTP_400_BAD_REQUEST)

       

    if job.lastDate < timezone.now():
        return Response({ 'error': 'You can not apply to this job. Deadline Reached' }, status=status.HTTP_400_BAD_REQUEST)

    alreadyApplied = job.candidatesapplied_set.filter(user=user).exists()

    if alreadyApplied:
      return Response({ 'error': 'You have already applied to this job.' }, status=status.HTTP_400_BAD_REQUEST)


    jobApplied = CandidatesApplied.objects.create(
      job = job,
      user = user,
      resume = user.userprofile.resume,
      academicPapers = user.userprofile.academicPapers,
      bankStatements = user.userprofile.bankStatements,
      approved=False,
      paid=False,
    )

    return Response({
      'applied': True,
      'job_id': jobApplied.id
    },
    status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCurrentUserAppliedJobs(request):

  args = { 'user_id': request.user.id }

  jobs = CandidatesApplied.objects.filter(**args)

  serializer = CandidatesAppliedSerializer(jobs, many=True)

  return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def isApplied(request, pk):

  user = request.user
  job = get_object_or_404(Job, id=pk)

  applied = job.candidatesapplied_set.filter(user=user).exists()

  return Response(applied)


#Get all the Jobs current user has created
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCurrentUserJobs(request):

    args = { 'user': request.user.id }

    jobs = Job.objects.filter(**args)
    serializer = JobSerializer(jobs, many=True)

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCandidatesApplied(request, pk):

    user = request.user
    job = get_object_or_404(Job, id=pk)

    if job.user != user:
        return Response({ 'error': 'You cannot access this job' }, status=status.HTTP_403_FORBIDDEN)

    candidates = job.candidatesapplied_set.all()

    serializer = CandidatesAppliedSerializer(candidates, many=True,)

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
  job = candidate.job
  approvedCount = CandidatesApplied.objects.filter(job=job, approved=True).count()
  if approvedCount >= job.positions:
      #Reject all other candidates who have applied to this job
    candidates_to_reject = CandidatesApplied.objects.filter(job=job, approved=False)
    for candidate in candidates_to_reject:
      candidate.rejected = True
      candidate.status = Status.Rejected
      candidate.save()

  
  # Update Positions Left
  positionsLeft = job.positions - approvedCount
  
  return Response({
      'positionsLeft': positionsLeft,
      'status': candidate.status,
      'approved': True,
      'application_id': candidate.job.id,
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
def isJobFull(request, job_id):
    job = Job.objects.get(id=job_id)
    is_full = job.isJobfull()
    data = {'is_full': is_full}
    return Response(data)

@api_view(['GET'])
def checkPositionsLeft(request, job_id):
    job = Job.objects.get(id=job_id)
    approved_count = CandidatesApplied.objects.filter(job=job, approved=True).count()
    positionsLeft = job.positions - approved_count
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
    paidCandidates = CandidatesApplied.objects.filter(paid=True)
    
    # Calculate total revenue from all paid candidates
    totalRevenue = sum(candidate.job.price for candidate in paidCandidates)

    # Get paid candidates within the last week
    lastWeek = timezone.now() - timezone.timedelta(days=7)
    recentPaidCandidates = paidCandidates.filter(appliedAt__gte=lastWeek)
    
    # Calculate total revenue from recent paid candidates
    recentRevenue = sum(candidate.job.price for candidate in recentPaidCandidates)
    
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
  






      










